from fastapi import APIRouter, Depends, HTTPException, Query
import unicodedata
import re
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
from mysql_lib import MySQLClient
from mysql_lib import list_users, update_user, get_user, list_products, create_product, update_product, delete_product, list_authors, list_publishers, list_categories, create_category, create_author, create_publisher, get_category, update_category, get_author, update_author, get_publisher, update_publisher, delete_category, delete_author, delete_publisher
from services.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

def slugify(text: str) -> str:
    """
    Convert a string to a slug.
    Normalize unicode, remove accents, convert to lowercase, 
    replace non-alphanumeric with hyphens.
    """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

@router.get("/stats/revenue")
def get_revenue_stats(
    period: str = Query(..., regex="^(day|week|month|year)$"),
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        date_format = ""
        if period == "day":
            date_format = "%Y-%m-%d"
        elif period == "week":
            date_format = "%Y-%u"
        elif period == "month":
            date_format = "%Y-%m"
        elif period == "year":
            date_format = "%Y"
            
        query = f"""
            SELECT 
                DATE_FORMAT(order_date, '{date_format}') as time_period,
                SUM(total_amount) as revenue,
                COUNT(id) as order_count
            FROM Orders
            WHERE status = 'delivered'
            GROUP BY time_period
            ORDER BY time_period DESC
            LIMIT 30
        """
        stats = client.fetch_query(query)
        return stats

@router.get("/stats/dashboard")
def get_dashboard_stats(current_user: dict = Depends(get_current_admin)):
    with MySQLClient() as client:
        # 1. Revenue (Current Month)
        revenue_query = """
            SELECT SUM(total_amount) as revenue
            FROM Orders
            WHERE status = 'delivered' 
            AND MONTH(order_date) = MONTH(CURRENT_DATE())
            AND YEAR(order_date) = YEAR(CURRENT_DATE())
        """
        revenue_result = client.fetch_one(revenue_query)
        revenue = revenue_result['revenue'] if revenue_result and revenue_result['revenue'] else 0

        # 2. New Orders (Pending)
        orders_query = "SELECT COUNT(id) as count FROM Orders WHERE status = 'pending'"
        orders_result = client.fetch_one(orders_query)
        new_orders = orders_result['count'] if orders_result else 0

        # 3. Total Products
        products_query = "SELECT COUNT(id) as count FROM Products"
        products_result = client.fetch_one(products_query)
        total_products = products_result['count'] if products_result else 0

        # 4. New Users (Current Month)
        users_query = """
            SELECT COUNT(id) as count 
            FROM Users 
            WHERE MONTH(created_at) = MONTH(CURRENT_DATE())
            AND YEAR(created_at) = YEAR(CURRENT_DATE())
        """
        users_result = client.fetch_one(users_query)
        new_users = users_result['count'] if users_result else 0

        return {
            "revenue": revenue,
            "new_orders": new_orders,
            "total_products": total_products,
            "new_users": new_users
        }

@router.get("/products")
def get_all_products(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        query = """
            SELECT 
                p.*, 
                a.name as author_name, 
                c.name as category_name, 
                pub.name as publisher_name
            FROM Products p
            LEFT JOIN Authors a ON p.author_id = a.id
            LEFT JOIN Categories c ON p.category_id = c.id
            LEFT JOIN Publishers pub ON p.publisher_id = pub.id
            LIMIT %s OFFSET %s
        """
        products = client.fetch_query(query, (limit, offset))
        return products

@router.get("/authors")
def get_authors(current_user: dict = Depends(get_current_admin)):
    with MySQLClient() as client:
        return list_authors(client)

@router.get("/publishers")
def get_publishers(current_user: dict = Depends(get_current_admin)):
    with MySQLClient() as client:
        return list_publishers(client)

@router.get("/categories")
def get_categories(current_user: dict = Depends(get_current_admin)):
    with MySQLClient() as client:
        return list_categories(client)

class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None

@router.post("/categories")
def create_new_category(
    category: CategoryCreate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        slug = category.slug
        if not slug:
            slug = slugify(category.name)
            
        category_id = create_category(
            client,
            name=category.name,
            slug=slug,
            description=category.description
        )
        return {"message": "Category created successfully", "category_id": category_id}

@router.get("/categories/{category_id}")
def get_category_detail(
    category_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        category = get_category(client, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

@router.put("/categories/{category_id}")
def update_existing_category(
    category_id: str,
    category: CategoryUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        update_data = {k: v for k, v in category.dict().items() if v is not None}
        if not update_data:
             raise HTTPException(status_code=400, detail="No data provided for update")
        
        # If name is updated but slug is not, regenerate slug? 
        # For now, let's only update slug if explicitly provided or if we want to enforce sync.
        # User requirement was "auto generate slug from name", usually implies on create. 
        # On update, we might want to keep existing slug unless changed.
        # Let's keep it simple: update what is sent.
        
        if 'name' in update_data and 'slug' not in update_data:
             # Optional: auto-update slug on name change? 
             # Let's NOT do that automatically to avoid breaking URLs.
             pass

        update_category(client, category_id, **update_data)
        return {"message": "Category updated successfully", "category_id": category_id}

@router.delete("/categories/{category_id}")
def delete_existing_category(
    category_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        # Optional: Check if used in products? 
        # DB has ON DELETE SET NULL, so it's safe to delete.
        delete_category(client, category_id)
        return {"message": "Category deleted successfully"}

class AuthorCreate(BaseModel):
    name: str
    year_of_birth: Optional[str] = None
    year_of_death: Optional[str] = None
    hometown: Optional[str] = None

@router.post("/authors")
def create_new_author(
    author: AuthorCreate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        author_id = create_author(
            client,
            name=author.name,
            year_of_birth=author.year_of_birth,
            year_of_death=author.year_of_death,
            hometown=author.hometown
        )
        return {"message": "Author created successfully", "author_id": author_id}

@router.get("/authors/{author_id}")
def get_author_detail(
    author_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        author = get_author(client, author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        return author

class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    year_of_birth: Optional[str] = None
    year_of_death: Optional[str] = None
    hometown: Optional[str] = None

@router.put("/authors/{author_id}")
def update_existing_author(
    author_id: str,
    author: AuthorUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        update_data = {k: v for k, v in author.dict().items() if v is not None}
        if not update_data:
             raise HTTPException(status_code=400, detail="No data provided for update")
        
        update_author(client, author_id, **update_data)
        return {"message": "Author updated successfully", "author_id": author_id}

@router.delete("/authors/{author_id}")
def delete_existing_author(
    author_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        delete_author(client, author_id)
        return {"message": "Author deleted successfully"}

class PublisherCreate(BaseModel):
    name: str
    address: Optional[str] = None

@router.post("/publishers")
def create_new_publisher(
    publisher: PublisherCreate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        publisher_id = create_publisher(
            client,
            name=publisher.name,
            address=publisher.address
        )
        return {"message": "Publisher created successfully", "publisher_id": publisher_id}

@router.get("/publishers/{publisher_id}")
def get_publisher_detail(
    publisher_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        publisher = get_publisher(client, publisher_id)
        if not publisher:
            raise HTTPException(status_code=404, detail="Publisher not found")
        return publisher

class PublisherUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

@router.put("/publishers/{publisher_id}")
def update_existing_publisher(
    publisher_id: str,
    publisher: PublisherUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        update_data = {k: v for k, v in publisher.dict().items() if v is not None}
        if not update_data:
             raise HTTPException(status_code=400, detail="No data provided for update")
        
        update_publisher(client, publisher_id, **update_data)
        return {"message": "Publisher updated successfully", "publisher_id": publisher_id}

@router.delete("/publishers/{publisher_id}")
def delete_existing_publisher(
    publisher_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        delete_publisher(client, publisher_id)
        return {"message": "Publisher deleted successfully"}

class ProductCreate(BaseModel):
    title: str
    price: Decimal
    category_id: str
    author_id: str
    publisher_id: str
    description: Optional[str] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[str] = None
    author_id: Optional[str] = None
    publisher_id: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None

@router.post("/products")
def create_new_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        product_id = create_product(
            client,
            title=product.title,
            price=product.price,
            category_id=product.category_id,
            author_id=product.author_id,
            publisher_id=product.publisher_id,
            description=product.description,
            stock_quantity=product.stock_quantity,
            image_url=product.image_url
        )
        return {"message": "Product created successfully", "product_id": product_id}

@router.put("/products/{product_id}")
def update_existing_product(
    product_id: str,
    product: ProductUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        update_data = {k: v for k, v in product.dict().items() if v is not None}
        if not update_data:
             raise HTTPException(status_code=400, detail="No data provided for update")
        
        update_product(client, product_id, **update_data)
        return {"message": "Product updated successfully", "product_id": product_id}

@router.delete("/products/{product_id}")
def delete_existing_product(
    product_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        delete_product(client, product_id)
        return {"message": "Product deleted successfully"}

@router.get("/users")
def get_all_users(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        users = list_users(client, limit=limit, offset=offset)
        return users

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

@router.put("/users/{user_id}")
def update_user_info(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        # Check if user exists
        existing_user = get_user(client, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Filter out None values
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        update_user(client, user_id, **update_data)
        
        return {"message": "User updated successfully", "user_id": user_id}

@router.get("/orders")
def get_all_orders(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        query = """
            SELECT 
                o.*, 
                u.fullname as customer_name 
            FROM Orders o
            LEFT JOIN Users u ON o.user_id = u.id
            ORDER BY o.order_date DESC
            LIMIT %s OFFSET %s
        """
        orders = client.fetch_query(query, (limit, offset))
        return orders

@router.get("/orders/{order_id}")
def get_order_detail(
    order_id: str,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        # Fetch order and user info
        order_query = """
            SELECT 
                o.*, 
                u.fullname as customer_name,
                u.email as customer_email,
                u.phone_number as customer_phone
            FROM Orders o
            LEFT JOIN Users u ON o.user_id = u.id
            WHERE o.id = %s
        """
        order = client.fetch_one(order_query, (order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Fetch order items with product info
        items_query = """
            SELECT 
                oi.*,
                p.title as product_title,
                p.image_url as product_image,
                p.author_id as product_author_id
            FROM OrderItems oi
            LEFT JOIN Products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """
        items = client.fetch_query(items_query, (order_id,))
        
        # Add items to order object
        order['items'] = items
        return order

class OrderUpdate(BaseModel):
    status: str
    admin_note: Optional[str] = None

from mysql_lib import update_order

@router.put("/orders/{order_id}")
def update_order_status(
    order_id: str,
    order_update: OrderUpdate,
    current_user: dict = Depends(get_current_admin)
):
    with MySQLClient() as client:
        # Verify order exists
        order_query = "SELECT id FROM Orders WHERE id = %s"
        if not client.fetch_one(order_query, (order_id,)):
             raise HTTPException(status_code=404, detail="Order not found")

        # Update status
        # Note: admin_note is not in the schema yet, so we only update status for now
        # If admin_note is added to DB, we can update it here.
        update_order(client, order_id, status=order_update.status)
        
        return {"message": "Order updated successfully", "order_id": order_id}
