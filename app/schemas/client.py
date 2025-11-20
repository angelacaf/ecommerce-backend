"""
Client Schemas - Validazione dati per Client
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class ClientBase(BaseModel):
    """Campi base del cliente"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    country: str = Field(default="Italy", max_length=100)


class ClientCreate(ClientBase):
    """Per registrare un nuovo cliente"""
    password: str = Field(..., min_length=6, max_length=100)


class ClientUpdate(BaseModel):
    """Per aggiornare un cliente (tutti i campi opzionali)"""
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


class ClientChangePassword(BaseModel):
    """Per cambiare password"""
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class ClientResponse(ClientBase):
    """Risposta API - include campi dal database (NO password_hash)"""
    id: int
    active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClientLogin(BaseModel):
    """Per login"""
    email: EmailStr
    password: str