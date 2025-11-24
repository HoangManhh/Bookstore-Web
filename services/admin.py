from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from mysql_lib.client import MySQLClient
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
