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
