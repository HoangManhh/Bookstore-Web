from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import auth, products, orders, users, admin

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Bookstore API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(admin.router)

# Mount Static Files (Frontend)
# Mount at root "/" to serve index.html automatically
app.mount("/", StaticFiles(directory="FE", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8036, reload=True)
