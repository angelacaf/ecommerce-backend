"""
Product Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    """Base product schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (must be > 0)")
    available_quantity: int = Field(0, ge=0, description="Available stock quantity")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    active: bool = Field(True, description="Whether product is active")
    featured: bool = Field(False, description="Whether product is featured")
    category_id: Optional[int] = Field(None, description="Category ID")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None
    featured: Optional[bool] = None
    category_id: Optional[int] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class ProductWithCategory(ProductResponse):
    """Product response with category details"""
    category_name: Optional[str] = None
    category_description: Optional[str] = None