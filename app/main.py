"""
FastAPI E-commerce Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api import products

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
    return {
        "message": "E-commerce API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ==================== INCLUDE ROUTERS ====================

# Products endpoints
app.include_router(products.router, prefix="/api", tags=["Products"])

# Quando aggiungerai altri modelli:
# app.include_router(users.router, prefix="/api", tags=["Users"])
# app.include_router(orders.router, prefix="/api", tags=["Orders"])
# app.include_router(categories.router, prefix="/api", tags=["Categories"])


# ==================== AVVIO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)