from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from mysql_lib.client import MySQLClient
from mysql_lib.crud import create_user, get_user_by_email
from services.auth import verify_password, create_access_token, get_password_hash
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    address: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=dict)
def register(user: UserRegister):
    with MySQLClient() as client:
        existing_user = get_user_by_email(client, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        user_id = create_user(
            client, 
            fullname=user.fullname, 
            email=user.email, 
            password=hashed_password,
            address=user.address,
            phone_number=user.phone_number
        )
        return {"message": "User registered successfully", "user_id": user_id}

@router.post("/login", response_model=Token)
def login(user: UserLogin):
    with MySQLClient() as client:
        db_user = get_user_by_email(client, user.email)
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": db_user["email"], "id": db_user["id"], "role": db_user["role"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
