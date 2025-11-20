import sys
import os

# Add the src directory to sys.path to allow importing mysql_lib
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from mysql_lib.client import MySQLClient
from mysql_lib.crud import (
    create_user, get_user, update_user, delete_user, list_users
)

def test_users_crud():
    print("Testing Users CRUD...")
    
    client = MySQLClient()
    
    try:
        # 1. Create
        print("Creating user...")
        user_id = create_user(
            client, 
            fullname="Test User", 
            email="test@example.com", 
            password="hashed_password", 
            address="123 Test St", 
            phone_number="1234567890"
        )
        print(f"User created with ID: {user_id}")
        
        # 2. Get
        print("Fetching user...")
        user = get_user(client, user_id)
        if user:
            print(f"User found: {user['fullname']} ({user['email']})")
        else:
            print("User not found!")
            return

        # 3. Update
        print("Updating user...")
        update_user(client, user_id, fullname="Updated Test User")
        updated_user = get_user(client, user_id)
        print(f"User updated: {updated_user['fullname']}")

        # 4. List
        print("Listing users...")
        users = list_users(client, limit=5)
        print(f"Found {len(users)} users.")

        # 5. Delete
        print("Deleting user...")
        delete_user(client, user_id)
        deleted_user = get_user(client, user_id)
        if not deleted_user:
            print("User deleted successfully.")
        else:
            print("Failed to delete user.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_users_crud()
