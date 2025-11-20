"""
Pydantic Schemas per validazione
"""
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from app.schemas.client import (  
    ClientBase,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientLogin,
    ClientChangePassword
)

__all__ = [
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientLogin",
    "ClientChangePassword"
]