from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db_connection import engine, Base
from app.api import products, users, orders, categories
from app.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS

# Crea tabelle database
Base.metadata.create_all(bind=engine)

# Inizializza FastAPI con security scheme
app = FastAPI(
    title=APP_NAME,
    description="Backend REST API per e-commerce con autenticazione JWT",
    version=APP_VERSION,
    swagger_ui_parameters={
        "persistAuthorization": True  # Mantiene il token anche dopo refresh
    }
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
                "verify_token": "GET /api/users/verify-token",
                "list": "GET /api/users (admin)",
                "get": "GET /api/users/{id} (admin)",
                "get_by_email": "GET /api/users/email/{email} (admin)",
                "delete": "DELETE /api/users/{id} (admin)"
            },
            "orders": {
                "create": "POST /api/orders (status: pending)",
                "initiate_payment": "POST /api/orders/{id}/initiate-payment",  # ← NUOVO
                "confirm_payment": "POST /api/orders/{id}/confirm-payment",     # ← NUOVO
                "list": "GET /api/orders (my orders)",
                "get": "GET /api/orders/{id}",
                "cancel": "DELETE /api/orders/{id} (pending only)",
                "list_all": "GET /api/orders/admin/all (admin)",               # ← NUOVO
                "list_user": "GET /api/orders/admin/{user_id}/orders (admin)", # ← NUOVO
                "update_status": "PATCH /api/orders/{id}/status (admin)"
            },
            "categories": {  
                "list": "GET /api/categories",
                "search": "GET /api/categories/search?q=sport",  
                "get": "GET /api/categories/{id}"
            }
        },
        "authentication": {
            "type": "Bearer JWT",
            "header": "Authorization: Bearer <token>",
            "obtain_token": "POST /api/users/login"
        },
        "payment": {  # ← NUOVO
            "provider": "Stripe",
            "flow": "1. Create order (pending) → 2. Initiate payment → 3. Pay on Stripe → 4. Confirm payment (paid)"
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