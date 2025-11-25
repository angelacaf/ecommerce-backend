"""
Pydantic Schemas per validazione
Esporta solo gli schemi effettivamente utilizzati nei router
"""

# Products
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

# Users
from app.schemas.user import (  
    UserRole,           # Per dependencies.py
    UserCreate,         # Per register
    UserUpdate,         # Per update profile
    User,               # Per /users/me e admin endpoints
    UserPublic,         # Dentro TokenWithUser
    UserLogin,          # Per login
    UserChangePassword, # Per change password
    TokenWithUser       # Per login/register response
)

# Orders
from app.schemas.order import (
    OrderItemCreate,
    OrderItemResponse,
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate
)

__all__ = [
    # Products
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    
    # Users
    "UserRole",
    "UserCreate",
    "UserUpdate",
    "User",
    "UserPublic",
    "UserLogin",
    "UserChangePassword",
    "TokenWithUser",
    
    # Orders
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderCreate",
    "OrderResponse",
    "OrderListResponse",
    "OrderStatusUpdate"
]