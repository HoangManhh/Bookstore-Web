from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from mysql_lib.client import MySQLClient
from mysql_lib.crud import get_user, update_user
from services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserProfile(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    address: Optional[str] = None
    phone_number: Optional[str] = None
    role: str

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

@router.get("/me", response_model=UserProfile)
def read_users_me(current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        user = get_user(client, current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@router.put("/me", response_model=dict)
def update_user_me(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    with MySQLClient() as client:
        # Filter out None values
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        if not update_data:
             return {"message": "No data to update"}
             
        update_user(client, current_user["id"], **update_data)
        return {"message": "User updated successfully"}
