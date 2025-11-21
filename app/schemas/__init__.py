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
from app.schemas.order import (
    OrderItemCreate,
    OrderItemResponse,
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate
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
    "ClientChangePassword",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderCreate",
    "OrderResponse",
    "OrderListResponse",
    "OrderStatusUpdate"
]