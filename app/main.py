from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product 

# Create FastAPI application
app = FastAPI(
    title="E-commerce API",
    description="API with PostgreSQL database",
    version="1.0.0"
)

# CORS CONFIGURATION
origins = [
    "http://localhost:3000",      # React
    "http://localhost:5173",      # Vite
    "http://localhost:4200",      # Angular
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],          # All headers
)

# ROOT ENDPOINT

@app.get("/")
def root():
    """Main page"""
    return {
        "message": "Welcome to E-commerce API!",
        "endpoints": {
            "products": "/api/products",
            "health": "/health",
            "docs": "/docs"
        }
    }

# PRODUCT ENDPOINTS

# POST   → Create a new product
# PUT    → Update an existing product
# DELETE → Delete a product
# GET    → Get product information (single or list)

@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    """
    Get all products from database.
    Uses Product Model to query PostgreSQL.
    """
    # Query with SQLAlchemy ORM
    products = db.query(Product).all()
    return products

@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a single product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return {"error": f"Product {product_id} not found"}
    
    return product

# HEALTH CHECK

@app.get("/health")
def health():
    """Check if API is active"""
    return {"status": "ok"}