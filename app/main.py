"""
FastAPI E-commerce Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api import products, clients

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
            "clients": {
                "register": "POST /api/clients/register",
                "login": "POST /api/clients/login",
                "list": "GET /api/clients",
                "get": "GET /api/clients/{id}",
                "get_by_email": "GET /api/clients/email/{email}",
                "update": "PUT /api/clients/{id}",
                "change_password": "POST /api/clients/{id}/change-password",
                "delete": "DELETE /api/clients/{id}"
            },
            "orders": {
                "note": "Coming soon..."
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

# Clients endpoints
app.include_router(clients.router, prefix="/api", tags=["Clients"])

# Orders endpoints (da implementare)
# app.include_router(orders.router, prefix="/api", tags=["Orders"])


# ==================== AVVIO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)