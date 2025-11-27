from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from mysql_lib.client import MySQLClient
from mysql_lib.crud import list_products, get_product, list_categories, get_category, list_authors, list_publishers, get_author, get_publisher

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

class Author(BaseModel):
    id: str
    name: str
    year_of_birth: Optional[date] = None
    year_of_death: Optional[date] = None
    hometown: Optional[str] = None

class Publisher(BaseModel):
    id: str
    name: str
    address: Optional[str] = None

@router.get("/", response_model=List[Product])
def get_products(
    limit: int = 100, 
    offset: int = 0,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    author_id: Optional[str] = None,
    publisher_id: Optional[str] = None,
    title: Optional[str] = None
):
    with MySQLClient() as client:
        query = "SELECT * FROM Products WHERE 1=1"
        params = []

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)
        
        if min_price is not None:
            query += " AND price >= %s"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= %s"
            params.append(max_price)
            
        if author_id:
            query += " AND author_id = %s"
            params.append(author_id)

        if publisher_id:
            query += " AND publisher_id = %s"
            params.append(publisher_id)

        if title:
            query += " AND title LIKE %s"
            params.append(f"%{title}%")

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        products = client.fetch_query(query, tuple(params))
            
        return products

@router.get("/categories", response_model=List[Category], tags=["categories"])
def get_categories():
    with MySQLClient() as client:
        return list_categories(client)

@router.get("/authors", response_model=List[Author], tags=["authors"])
def get_authors():
    with MySQLClient() as client:
        return list_authors(client)

@router.get("/publishers", response_model=List[Publisher], tags=["publishers"])
def get_publishers():
    with MySQLClient() as client:
        return list_publishers(client)

@router.get("/categories/{category_id}", response_model=Category, tags=["categories"])
def get_category_detail(category_id: str):
    with MySQLClient() as client:
        category = get_category(client, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

@router.get("/authors/{author_id}", response_model=Author, tags=["authors"])
def get_author_detail(author_id: str):
    with MySQLClient() as client:
        author = get_author(client, author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        return author

@router.get("/publishers/{publisher_id}", response_model=Publisher, tags=["publishers"])
def get_publisher_detail(publisher_id: str):
    with MySQLClient() as client:
        publisher = get_publisher(client, publisher_id)
        if not publisher:
            raise HTTPException(status_code=404, detail="Publisher not found")
        return publisher

@router.get("/{product_id}", response_model=Product)
def get_product_detail(product_id: str):
    with MySQLClient() as client:
        product = get_product(client, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
