"""
Users API Router con JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db_connection import get_db
from app.schemas.user import (
    UserCreate,  
    UserUpdate,
    UserResponse,
    UserLogin,
    UserChangePassword,
    Token  
)
from app.crud import user as crud_user
from app.utils.auth import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES  
from app.utils.dependencies import get_current_user, require_admin  
from app.models.user import User

router = APIRouter()

# ==================== REGISTRAZIONE & LOGIN ====================

@router.post("/users/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra nuovo utente e restituisce token JWT"""
    existing_user = crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    # Crea utente
    new_user = crud_user.create_user(db, user)
    
    # Crea token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),  # ✅ Converti in stringa
            "email": new_user.email,
            "role": new_user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/users/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login utente e restituisce token JWT"""
    user = crud_user.get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti"
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti"
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disattivato"
        )
    
    # Crea token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # ✅ Converti in stringa
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# ==================== PROFILO UTENTE ====================

@router.get("/users/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):  
    """Ottieni profilo utente autenticato"""
    return current_user


@router.put("/users/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Aggiorna profilo utente autenticato"""
    updated_user = crud_user.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return updated_user


@router.post("/users/me/change-password", response_model=UserResponse)
def change_my_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    """Cambia password utente autenticato"""
    user = crud_user.change_password(
        db,
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password attuale non corretta"
        )
    return user


# ==================== ADMIN ENDPOINTS ====================

@router.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    current_user: User = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Lista utenti (SOLO ADMIN)"""
    return crud_user.get_users(db, skip, limit, active_only)


@router.get("/users/email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """Ottieni utente per email (SOLO ADMIN)"""
    user = crud_user.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Dettaglio utente (SOLO ADMIN)"""
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """Elimina utente (SOLO ADMIN)"""
    if not crud_user.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )