"""
User Schemas - Validazione dati per User
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from enum import Enum


class UserRole(str, Enum):
    """Ruoli utente"""
    ADMIN = "admin"
    CUSTOMER = "customer"


class UserBase(BaseModel):
    """Campi base dell'utente"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    country: str = Field(default="Italy", max_length=100)


class UserCreate(UserBase):
    """Per registrare un nuovo utente"""
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = Field(default="customer")  


class UserUpdate(BaseModel):
    """Per aggiornare un utente (tutti i campi opzionali)"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserChangePassword(BaseModel):
    """Per cambiare password"""
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    """Risposta API - include campi dal database (NO password_hash)"""
    id: int
    role: UserRole 
    active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Per login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Risposta token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Dati contenuti nel token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None