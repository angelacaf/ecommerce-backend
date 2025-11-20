"""
Product Schemas - Validazione dati per Product
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    """Campi base del prodotto"""
    name: str
    description: Optional[str] = None
    price: float
    available_quantity: int = 0
    image_url: Optional[str] = None
    sku: Optional[str] = None
    active: bool = True
    featured: bool = False


class ProductCreate(ProductBase):
    """Per creare un prodotto nuovo"""
    pass


class ProductUpdate(BaseModel):
    """Per aggiornare un prodotto (tutti i campi opzionali)"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available_quantity: Optional[int] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    active: Optional[bool] = None
    featured: Optional[bool] = None


class ProductResponse(ProductBase):
    """Risposta API - include campi dal database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)