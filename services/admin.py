from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from mysql_lib import MySQLClient
from mysql_lib import list_users, update_user, get_user
from services.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

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
            WHERE status != 'cancelled'
            GROUP BY time_period
            ORDER BY time_period DESC
            LIMIT 30
        """
        stats = client.fetch_query(query)
        return stats

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
