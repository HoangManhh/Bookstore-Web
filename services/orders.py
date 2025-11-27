from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from mysql_lib.client import MySQLClient
import uuid
from decimal import Decimal
from services.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: Decimal

class OrderCreate(BaseModel):
    # user_id is removed, we get it from token
    shipping_address: str
    shipping_phone: str
    payment_method: str
    items: List[OrderItemCreate]

@router.post("/", status_code=201)
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        try:
            client.start_transaction()

            # 1. Calculate Total Amount & Validate Stock
            total_amount = Decimal(0)
            
            # Check stock for all items first
            for item in order.items:
                # Check stock
                check_stock_query = "SELECT stock_quantity FROM Products WHERE id = %s FOR UPDATE"
                result = client.fetch_query(check_stock_query, (item.product_id,))
                
                if not result:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                
                current_stock = result[0]['stock_quantity']
                if current_stock < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}. Available: {current_stock}")

                total_amount += item.price * item.quantity

            # 2. Create Order
            order_id = str(uuid.uuid4())
            query_order = """
                INSERT INTO Orders (id, user_id, total_amount, shipping_address, shipping_phone, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            client.execute_query(query_order, (
                order_id, 
                current_user['id'], 
                total_amount, 
                order.shipping_address, 
                order.shipping_phone, 
                order.payment_method
            ))

            # 3. Create Order Items and Deduct Stock
            query_item = """
                INSERT INTO OrderItems (id, order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s, %s)
            """
            update_stock_query = """
                UPDATE Products SET stock_quantity = stock_quantity - %s WHERE id = %s
            """

            for item in order.items:
                item_id = str(uuid.uuid4())
                # Insert Order Item
                client.execute_query(query_item, (
                    item_id, 
                    order_id, 
                    item.product_id, 
                    item.quantity, 
                    item.price
                ))
                # Deduct Stock
                client.execute_query(update_stock_query, (item.quantity, item.product_id))

            client.commit()
            return {"id": order_id, "message": "Order created successfully"}
        
        except Exception as e:
            client.rollback()
            raise e

@router.get("/me", response_model=List[dict])
def read_user_orders(current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        # 1. Fetch Orders (excluding cancelled)
        query_orders = """
            SELECT id, order_date, status, total_amount, shipping_address, shipping_phone, payment_method
            FROM Orders 
            WHERE user_id = %s AND status != 'cancelled'
            ORDER BY order_date DESC
        """
        orders = client.fetch_query(query_orders, (current_user['id'],))
        
        # 2. Fetch Items for each order
        for order in orders:
            query_items = """
                SELECT oi.quantity, p.title 
                FROM OrderItems oi 
                LEFT JOIN Products p ON oi.product_id = p.id 
                WHERE oi.order_id = %s
            """
            items = client.fetch_query(query_items, (order['id'],))
            order['items'] = items
            
        return orders

@router.put("/{order_id}/cancel")
def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        try:
            client.start_transaction()
            
            # 1. Check Order Status and Ownership
            query_check = "SELECT user_id, status FROM Orders WHERE id = %s FOR UPDATE"
            order = client.fetch_query(query_check, (order_id,))
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            if order[0]['user_id'] != current_user['id']:
                raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
            
            if order[0]['status'] in ['delivered', 'cancelled']:
                raise HTTPException(status_code=400, detail="Cannot cancel delivered or already cancelled order")

            # 2. Update Status
            query_update = "UPDATE Orders SET status = 'cancelled' WHERE id = %s"
            client.execute_query(query_update, (order_id,))
            
            # 3. Restore Stock
            query_items = "SELECT product_id, quantity FROM OrderItems WHERE order_id = %s"
            items = client.fetch_query(query_items, (order_id,))
            
            update_stock = "UPDATE Products SET stock_quantity = stock_quantity + %s WHERE id = %s"
            for item in items:
                client.execute_query(update_stock, (item['quantity'], item['product_id']))
                
            client.commit()
            return {"message": "Order cancelled successfully"}
            
        except Exception as e:
            client.rollback()
            raise e

@router.get("/{order_id}")
def read_order_details(order_id: str, current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        # 1. Fetch Order
        query_order = """
            SELECT id, order_date, status, total_amount, shipping_address, shipping_phone, payment_method, user_id
            FROM Orders 
            WHERE id = %s
        """
        order = client.fetch_query(query_order, (order_id,))
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        if order[0]['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 2. Fetch Items
        query_items = """
            SELECT oi.product_id, oi.quantity, oi.price_at_purchase, p.title, p.image_url, p.price as current_price, p.stock_quantity
            FROM OrderItems oi 
            LEFT JOIN Products p ON oi.product_id = p.id 
            WHERE oi.order_id = %s
        """
        items = client.fetch_query(query_items, (order_id,))
        order[0]['items'] = items
        
        return order[0]

class OrderItemUpdate(BaseModel):
    product_id: str
    quantity: int

@router.put("/{order_id}/items")
def update_order_items(order_id: str, new_items: List[OrderItemUpdate], current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        try:
            client.start_transaction()
            
            # 1. Check Order
            query_check = "SELECT user_id, status FROM Orders WHERE id = %s FOR UPDATE"
            order = client.fetch_query(query_check, (order_id,))
            
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            if order[0]['user_id'] != current_user['id']:
                raise HTTPException(status_code=403, detail="Not authorized")
            if order[0]['status'] in ['delivered', 'cancelled']:
                raise HTTPException(status_code=400, detail="Cannot edit delivered or cancelled order")

            # 2. Get Current Items
            query_current_items = "SELECT product_id, quantity, price_at_purchase FROM OrderItems WHERE order_id = %s"
            current_items_list = client.fetch_query(query_current_items, (order_id,))
            current_items_map = {item['product_id']: item for item in current_items_list}
            
            # 3. Process Updates
            total_amount = Decimal(0)
            
            # 3a. Handle New and Updated Items
            for new_item in new_items:
                pid = new_item.product_id
                qty = new_item.quantity
                
                if qty <= 0:
                    continue # Should be handled by removal logic if it was present, or ignored if new
                
                # Check product info (price, stock)
                query_product = "SELECT price, stock_quantity FROM Products WHERE id = %s FOR UPDATE"
                product = client.fetch_query(query_product, (pid,))
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {pid} not found")
                
                current_price = product[0]['price']
                current_stock = product[0]['stock_quantity']
                
                if pid in current_items_map:
                    # Update existing item
                    old_qty = current_items_map[pid]['quantity']
                    price = current_items_map[pid]['price_at_purchase'] # Keep original price
                    diff = qty - old_qty
                    
                    if diff > 0:
                        if current_stock < diff:
                            raise HTTPException(status_code=400, detail=f"Insufficient stock for {pid}")
                        # Deduct stock
                        client.execute_query("UPDATE Products SET stock_quantity = stock_quantity - %s WHERE id = %s", (diff, pid))
                    elif diff < 0:
                        # Restore stock
                        client.execute_query("UPDATE Products SET stock_quantity = stock_quantity + %s WHERE id = %s", (abs(diff), pid))
                        
                    # Update OrderItem
                    client.execute_query("UPDATE OrderItems SET quantity = %s WHERE order_id = %s AND product_id = %s", (qty, order_id, pid))
                    
                    total_amount += price * qty
                    
                    # Remove from map to mark as processed
                    del current_items_map[pid]
                    
                else:
                    # Add new item
                    if current_stock < qty:
                        raise HTTPException(status_code=400, detail=f"Insufficient stock for {pid}")
                    
                    # Deduct stock
                    client.execute_query("UPDATE Products SET stock_quantity = stock_quantity - %s WHERE id = %s", (qty, pid))
                    
                    # Insert OrderItem
                    item_id = str(uuid.uuid4())
                    client.execute_query(
                        "INSERT INTO OrderItems (id, order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s, %s)",
                        (item_id, order_id, pid, qty, current_price)
                    )
                    
                    total_amount += current_price * qty

            # 3b. Handle Removed Items (remaining in current_items_map)
            for pid, item in current_items_map.items():
                # Restore stock
                client.execute_query("UPDATE Products SET stock_quantity = stock_quantity + %s WHERE id = %s", (item['quantity'], pid))
                # Delete OrderItem
                client.execute_query("DELETE FROM OrderItems WHERE order_id = %s AND product_id = %s", (order_id, pid))

            # 4. Update Order Total
            client.execute_query("UPDATE Orders SET total_amount = %s WHERE id = %s", (total_amount, order_id))
            
            client.commit()
            return {"message": "Order updated successfully"}
            
        except Exception as e:
            client.rollback()
            raise e
