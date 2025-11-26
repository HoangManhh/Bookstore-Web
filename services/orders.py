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
        # 1. Calculate Total Amount
        total_amount = sum(item.price * item.quantity for item in order.items)

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

        # 3. Create Order Items
        query_item = """
            INSERT INTO OrderItems (id, order_id, product_id, quantity, price_at_purchase)
            VALUES (%s, %s, %s, %s, %s)
        """
        for item in order.items:
            item_id = str(uuid.uuid4())
            client.execute_query(query_item, (
                item_id, 
                order_id, 
                item.product_id, 
                item.quantity, 
                item.price
            ))

        return {"id": order_id, "message": "Order created successfully"}
