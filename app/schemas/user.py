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


# ========================================
# BASE SCHEMAS (per input)
# ========================================

class UserBase(BaseModel):
    """Campi base condivisi tra gli schemi"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema per registrazione nuovo utente"""
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    country: str = Field(default="Italy", max_length=100)
    role: UserRole = Field(default=UserRole.CUSTOMER)


class UserUpdate(BaseModel):
    """Schema per aggiornamento utente (tutti i campi opzionali)"""
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
    """Schema per cambio password"""
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


# ========================================
# RESPONSE SCHEMAS (per output)
# ========================================

class UserPublic(UserBase):
    """
    Schema pubblico utente - dati minimi per autenticazione
    Usato nelle risposte di login/register
    """
    id: int
    role: UserRole
    
    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """
    Schema completo utente
    Usato per /users/me e endpoint admin
    """
    id: int
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None
    country: str
    role: UserRole
    active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========================================
# AUTHENTICATION SCHEMAS
# ========================================

class Token(BaseModel):
    """Schema standard OAuth2 token response (solo token)"""
    access_token: str
    token_type: str = "bearer"


class TokenWithUser(Token):
    """
    Token con dati utente pubblici
    Usato per risposta di login/register
    """
    user: UserPublic


class TokenData(BaseModel):
    """
    Payload del JWT token (per uso interno)
    Rappresenta i dati decodificati dal token
    """
    sub: str  # Standard OAuth2: subject (user_id come stringa)
    email: Optional[str] = None
    role: Optional[UserRole] = None


class UserLogin(BaseModel):
    """
    Schema per login (alternativo a OAuth2PasswordRequestForm)
    """
    email: EmailStr
    password: str