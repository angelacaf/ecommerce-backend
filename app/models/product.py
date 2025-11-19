from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    """Model for products table"""
    
    # Table name in database - METADATA (configuration)
    __tablename__ = "products"
    
    # Columns (as in PostgreSQL table) - COLUMN DESCRIPTORS (map SQL columns)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    available_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500))
    sku = Column(String(100), unique=True)
    active = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())