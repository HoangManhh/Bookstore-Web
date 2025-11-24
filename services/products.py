from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from mysql_lib.client import MySQLClient
from mysql_lib.crud import list_products, get_product, list_categories

router = APIRouter(prefix="/products", tags=["products"])

class Product(BaseModel):
    id: str
    title: str
    price: float
    image_url: Optional[str] = None
    category_id: Optional[str] = None
    author_id: Optional[str] = None
    publisher_id: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: int

class Category(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None

@router.get("/", response_model=List[Product])
def get_products(
    limit: int = 100, 
    offset: int = 0,
    category_id: Optional[str] = None
):
    with MySQLClient() as client:
        # Note: list_products in crud.py doesn't support filtering by category yet.
        # We might need to extend it or filter in python (less efficient) or write a custom query here.
        # For now, let's use list_products and filter if needed, or better, extend the query.
        
        if category_id:
             query = "SELECT * FROM Products WHERE category_id = %s LIMIT %s OFFSET %s"
             products = client.fetch_query(query, (category_id, limit, offset))
        else:
            products = list_products(client, limit, offset)
            
        return products

@router.get("/{product_id}", response_model=Product)
def get_product_detail(product_id: str):
    with MySQLClient() as client:
        product = get_product(client, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

@router.get("/categories", response_model=List[Category], tags=["categories"])
def get_categories():
    with MySQLClient() as client:
        return list_categories(client)
