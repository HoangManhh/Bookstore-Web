from typing import List, Optional, Dict, Any
from .client import MySQLClient
from .utils import generate_uuid

# --- Users ---
def create_user(client: MySQLClient, fullname: str, email: str, password: str, address: str = None, phone_number: str = None, role: str = 'customer', status: str = 'active') -> str:
    user_id = generate_uuid()
    query = """
        INSERT INTO Users (id, fullname, email, password, address, phone_number, role, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    client.execute_query(query, (user_id, fullname, email, password, address, phone_number, role, status))
    return user_id

def get_user(client: MySQLClient, user_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Users WHERE id = %s"
    return client.fetch_one(query, (user_id,))

def get_user_by_email(client: MySQLClient, email: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Users WHERE email = %s"
    return client.fetch_one(query, (email,))

def update_user(client: MySQLClient, user_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    query = f"UPDATE Users SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_user(client: MySQLClient, user_id: str) -> int:
    query = "DELETE FROM Users WHERE id = %s"
    return client.execute_query(query, (user_id,))

def list_users(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Users LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- Authors ---
def create_author(client: MySQLClient, name: str, year_of_birth: str = None, year_of_death: str = None, hometown: str = None) -> str:
    author_id = generate_uuid()
    query = """
        INSERT INTO Authors (id, name, year_of_birth, year_of_death, hometown)
        VALUES (%s, %s, %s, %s, %s)
    """
    client.execute_query(query, (author_id, name, year_of_birth, year_of_death, hometown))
    return author_id

def get_author(client: MySQLClient, author_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Authors WHERE id = %s"
    return client.fetch_one(query, (author_id,))

def update_author(client: MySQLClient, author_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(author_id)
    query = f"UPDATE Authors SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_author(client: MySQLClient, author_id: str) -> int:
    query = "DELETE FROM Authors WHERE id = %s"
    return client.execute_query(query, (author_id,))

def list_authors(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Authors LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- Publishers ---
def create_publisher(client: MySQLClient, name: str, address: str = None) -> str:
    publisher_id = generate_uuid()
    query = "INSERT INTO Publishers (id, name, address) VALUES (%s, %s, %s)"
    client.execute_query(query, (publisher_id, name, address))
    return publisher_id

def get_publisher(client: MySQLClient, publisher_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Publishers WHERE id = %s"
    return client.fetch_one(query, (publisher_id,))

def update_publisher(client: MySQLClient, publisher_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(publisher_id)
    query = f"UPDATE Publishers SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_publisher(client: MySQLClient, publisher_id: str) -> int:
    query = "DELETE FROM Publishers WHERE id = %s"
    return client.execute_query(query, (publisher_id,))

def list_publishers(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Publishers LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- Categories ---
def create_category(client: MySQLClient, name: str, slug: str, description: str = None) -> str:
    category_id = generate_uuid()
    query = "INSERT INTO Categories (id, name, slug, description) VALUES (%s, %s, %s, %s)"
    client.execute_query(query, (category_id, name, slug, description))
    return category_id

def get_category(client: MySQLClient, category_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Categories WHERE id = %s"
    return client.fetch_one(query, (category_id,))

def update_category(client: MySQLClient, category_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(category_id)
    query = f"UPDATE Categories SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_category(client: MySQLClient, category_id: str) -> int:
    query = "DELETE FROM Categories WHERE id = %s"
    return client.execute_query(query, (category_id,))

def list_categories(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Categories LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- Products ---
def create_product(client: MySQLClient, title: str, price: float, category_id: str = None, author_id: str = None, publisher_id: str = None, description: str = None, stock_quantity: int = 0, image_url: str = None) -> str:
    product_id = generate_uuid()
    query = """
        INSERT INTO Products (id, category_id, author_id, publisher_id, title, description, price, stock_quantity, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    client.execute_query(query, (product_id, category_id, author_id, publisher_id, title, description, price, stock_quantity, image_url))
    return product_id

def get_product(client: MySQLClient, product_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Products WHERE id = %s"
    return client.fetch_one(query, (product_id,))

def update_product(client: MySQLClient, product_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(product_id)
    query = f"UPDATE Products SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_product(client: MySQLClient, product_id: str) -> int:
    query = "DELETE FROM Products WHERE id = %s"
    return client.execute_query(query, (product_id,))

def list_products(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Products LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- Orders ---
def create_order(client: MySQLClient, user_id: str, total_amount: float, shipping_address: str, payment_method: str, shipping_phone: str = None, status: str = 'pending') -> str:
    order_id = generate_uuid()
    query = """
        INSERT INTO Orders (id, user_id, status, total_amount, shipping_address, shipping_phone, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    client.execute_query(query, (order_id, user_id, status, total_amount, shipping_address, shipping_phone, payment_method))
    return order_id

def get_order(client: MySQLClient, order_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM Orders WHERE id = %s"
    return client.fetch_one(query, (order_id,))

def update_order(client: MySQLClient, order_id: str, **kwargs) -> int:
    if not kwargs:
        return 0
    set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(order_id)
    query = f"UPDATE Orders SET {set_clause} WHERE id = %s"
    return client.execute_query(query, tuple(values))

def delete_order(client: MySQLClient, order_id: str) -> int:
    query = "DELETE FROM Orders WHERE id = %s"
    return client.execute_query(query, (order_id,))

def list_orders(client: MySQLClient, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Orders LIMIT %s OFFSET %s"
    return client.fetch_query(query, (limit, offset))

# --- OrderItems ---
def add_order_item(client: MySQLClient, order_id: str, product_id: str, quantity: int, price_at_purchase: float) -> str:
    item_id = generate_uuid()
    query = """
        INSERT INTO OrderItems (id, order_id, product_id, quantity, price_at_purchase)
        VALUES (%s, %s, %s, %s, %s)
    """
    client.execute_query(query, (item_id, order_id, product_id, quantity, price_at_purchase))
    return item_id

def get_order_items(client: MySQLClient, order_id: str) -> List[Dict[str, Any]]:
    query = "SELECT * FROM OrderItems WHERE order_id = %s"
    return client.fetch_query(query, (order_id,))

# --- Comments ---
def add_comment(client: MySQLClient, product_id: str, user_id: str, comment: str) -> str:
    comment_id = generate_uuid()
    query = """
        INSERT INTO Comments (id, product_id, user_id, comment)
        VALUES (%s, %s, %s, %s)
    """
    client.execute_query(query, (comment_id, product_id, user_id, comment))
    return comment_id

def get_product_comments(client: MySQLClient, product_id: str) -> List[Dict[str, Any]]:
    query = "SELECT * FROM Comments WHERE product_id = %s"
    return client.fetch_query(query, (product_id,))
