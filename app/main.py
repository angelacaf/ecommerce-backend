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

# ==================== ENDPOINTS ====================

@app.get("/")
def home():
    """Homepage API con link alla documentazione"""
    return {
        "message": "E-commerce API",
        "version": APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}


# ==================== ROUTERS ====================

app.include_router(products.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(categories.router, prefix="/api")


# ==================== AVVIO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)