from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db_connection import engine, Base
from app.api import products, users, orders, categories
from app.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS

# Crea tabelle database
Base.metadata.create_all(bind=engine)

# Inizializza FastAPI
app = FastAPI(
    title=APP_NAME,
    description="Backend REST API per e-commerce",
    version=APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
                "search": "GET /api/products/search?q=shirt",
                "get": "GET /api/products/{id}",
                "get_by_sku": "GET /api/products/sku/{sku}",  
                "create": "POST /api/products",
                "update": "PUT /api/products/{id}",
                "delete": "DELETE /api/products/{id}"
            },
            "users": {
                "register": "POST /api/users/register",
                "login": "POST /api/users/login",
                "profile": "GET /api/users/me",  
                "update_profile": "PUT /api/users/me",  
                "change_my_password": "POST /api/users/me/change-password",  
                "list": "GET /api/users (admin)",
                "get": "GET /api/users/{id} (admin)",
                "get_by_email": "GET /api/users/email/{email} (admin)",
                "delete": "DELETE /api/users/{id} (admin)"
            },
            "orders": {
                "create": "POST /api/orders",
                "list": "GET /api/orders",
                "get": "GET /api/orders/{id}",
                "update_status": "PATCH /api/orders/{id}/status (admin)",
                "cancel": "DELETE /api/orders/{id}"
            },
            "categories": {  
                "list": "GET /api/categories",
                "search": "GET /api/categories/search?q=sport",  
                "get": "GET /api/categories/{id}"
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
        "version": "1.0.0",
        "database": "connected"
    }


# ==================== INCLUDE ROUTERS ====================

# Products endpoints
app.include_router(products.router, prefix="/api", tags=["Products"])

# Users endpoints
app.include_router(users.router, prefix="/api", tags=["Users"])

# Orders endpoints
app.include_router(orders.router, prefix="/api", tags=["Orders"])

# Categories endpoints  
app.include_router(categories.router, prefix="/api", tags=["Categories"])


# ==================== AVVIO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True  
    )