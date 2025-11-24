"""
FastAPI E-commerce Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db_connection import engine, Base
from app.api import products, users, orders

# Crea tabelle database
Base.metadata.create_all(bind=engine)

# Inizializza FastAPI
app = FastAPI(
    title="E-commerce API",
    description="Backend REST API per e-commerce",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HOME ====================

@app.get("/")
def home():
    """
    Endpoint root - Restituisce informazioni sull'API e lista degli endpoint disponibili
    """
    return {
        "message": "E-commerce API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "products": {
                "list": "GET /api/products",
                "get": "GET /api/products/{id}",
                "create": "POST /api/products",
                "update": "PUT /api/products/{id}",
                "delete": "DELETE /api/products/{id}"
            },
            "users": {
                "register": "POST /api/users/register",
                "login": "POST /api/users/login",
                "list": "GET /api/users",
                "get": "GET /api/users/{id}",
                "get_by_email": "GET /api/users/email/{email}",
                "update": "PUT /api/users/{id}",
                "change_password": "POST /api/users/{id}/change-password",
                "delete": "DELETE /api/users/{id}"
            },
            "orders": {
                "create": "POST /api/orders",
                "list": "GET /api/orders",
                "get": "GET /api/orders/{id}",
                "update_status": "PATCH /api/orders/{id}/status",
                "cancel": "DELETE /api/orders/{id}"
            }
        },
        "status": "running"
    }


# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    """
    Health check endpoint - per verificare che l'API sia online
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# ==================== INCLUDE ROUTERS ====================

# Products endpoints
app.include_router(products.router, prefix="/api", tags=["Products"])

# users endpoints
app.include_router(users.router, prefix="/api", tags=["users"])

# Orders endpoints
app.include_router(orders.router, prefix="/api", tags=["Orders"])


# ==================== AVVIO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)