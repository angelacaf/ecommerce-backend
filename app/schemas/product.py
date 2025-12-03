"""
Product Schemas - Validazione dati per Product
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ============== CATEGORY IN PRODUCT ==============
class CategoryInProduct(BaseModel):
    """Schema categoria per includere nei prodotti"""
    id: int
    name: str
    description: Optional[str] = None
    active: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============== PRODUCT SCHEMAS ==============
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
    category_id: Optional[int] = None  # ✅ AGGIUNTO


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
    category_id: Optional[int] = None  # ✅ AGGIUNTO


class ProductResponse(ProductBase):
    """Risposta API - include campi dal database + categoria"""
    id: int
    category: Optional[CategoryInProduct] = None  # ✅ AGGIUNTO - Oggetto categoria completo
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)