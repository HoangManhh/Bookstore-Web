from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from mysql_lib.client import MySQLClient
from mysql_lib.crud import create_user, get_user_by_email

# Configuration
SECRET_KEY = "4rQgHMGVXGNV9UbcUZqwGHrMga1ahd3RUc9GLkHkgZo"  # In production, get this from env variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Using Argon2 - no 72-byte password limitation
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Models ---
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

# --- Helper Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        role: str = payload.get("role")
        if email is None or user_id is None:
            raise credentials_exception
        return {"email": email, "id": user_id, "role": role}
    except JWTError:
        raise credentials_exception

# --- Endpoints ---
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
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user["email"], "id": db_user["id"], "role": db_user["role"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

# OAuth2-compliant token endpoint (for frontend login)
@router.post("/token", response_model=Token)
def get_token(username: str = Form(...), password: str = Form(...)):
    """
    OAuth2-compliant token endpoint.
    Accepts form data with 'username' (email) and 'password'.
    """
    with MySQLClient() as client:
        db_user = get_user_by_email(client, username)  # username is actually email
        if not db_user or not verify_password(password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user["email"], "id": db_user["id"], "role": db_user["role"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

# ⚠️ DEVELOPMENT ONLY - Remove this endpoint in production!
@router.post("/create-admin", response_model=dict)
def create_admin(user: UserRegister):
    """
    Create an admin user. 
    ⚠️ WARNING: This endpoint should ONLY be used in development!
    Remove or disable this in production environment.
    """
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
            phone_number=user.phone_number,
            role="admin",  # Force role to admin
            status="active"
        )
        return {
            "message": "Admin user created successfully", 
            "user_id": user_id,
            "role": "admin"
        }
