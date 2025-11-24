"""
Category Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class CategoryBase(BaseModel):
    """Base category schema with common fields"""
    name: str
    description: Optional[str] = None
    active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)