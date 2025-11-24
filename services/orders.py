from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from mysql_lib.client import MySQLClient
from mysql_lib.crud import create_order, add_order_item, get_order, list_orders, get_order_items
from services.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    total_amount: float
    shipping_address: str
    shipping_phone: Optional[str] = None
    payment_method: str

class OrderItem(BaseModel):
    id: str
    product_id: str
    quantity: int
    price_at_purchase: float

class Order(BaseModel):
    id: str
    user_id: str
    status: str
    total_amount: float
    shipping_address: str
    payment_method: str
    created_at: Optional[str] = None # In DB it is TIMESTAMP, might come as datetime or str

@router.post("/", response_model=dict)
def create_new_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with MySQLClient() as client:
        # Start transaction logic could be here, but for now simple sequential inserts
        order_id = create_order(
            client,
            user_id=user_id,
            total_amount=order.total_amount,
            shipping_address=order.shipping_address,
            shipping_phone=order.shipping_phone,
            payment_method=order.payment_method
        )
        
        for item in order.items:
            add_order_item(
                client,
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price
            )
            
        return {"message": "Order created successfully", "order_id": order_id}

@router.get("/my-orders", response_model=List[Order])
def get_my_orders(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with MySQLClient() as client:
        # Custom query for user orders
        query = "SELECT * FROM Orders WHERE user_id = %s ORDER BY order_date DESC"
        orders = client.fetch_query(query, (user_id,))
        return orders

@router.get("/{order_id}", response_model=Order)
def get_order_detail(order_id: str, current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        order = get_order(client, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check ownership or admin
        if order["user_id"] != current_user["id"] and current_user["role"] != "admin":
             raise HTTPException(status_code=403, detail="Not authorized to view this order")
             
        return order
