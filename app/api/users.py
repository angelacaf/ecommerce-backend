"""
users API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db_connection import get_db
from app.schemas.user import (
    userCreate, 
    userUpdate, 
    userResponse, 
    userLogin,
    userChangePassword
)
from app.crud import user as crud_user

# Crea router per users
router = APIRouter()


# ==================== REGISTRAZIONE & LOGIN ====================

@router.post("/users/register", response_model=userResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: userCreate, db: Session = Depends(get_db)):
    """
    Registra un nuovo usere
    
    - Verifica che l'email non sia già registrata
    - Hash della password
    - Crea il nuovo usere
    """
    # Verifica se email già esiste
    existing_user = crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    return crud_user.create_user(db, user)


@router.post("/users/login", response_model=userResponse)
def login_user(credentials: userLogin, db: Session = Depends(get_db)):
    """
    Login usere
    
    - Verifica email e password
    - Restituisce i dati del usere (in produzione restituirebbe un JWT token)
    """
    user = crud_user.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti"
        )
    
    return user


# ==================== CRUD users ====================

@router.get("/users", response_model=list[userResponse])
def list_users(skip: int = 0, limit: int = 20, active_only: bool = True, db: Session = Depends(get_db)):
    """
    Lista useri
    
    - skip: numero di record da saltare (per paginazione)
    - limit: numero massimo di record da restituire
    - active_only: se True, restituisce solo useri attivi
    """
    return crud_user.get_users(db, skip, limit, active_only)


@router.get("/users/{user_id}", response_model=userResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Dettaglio usere"""
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usere non trovato"
        )
    return user


@router.get("/users/email/{email}", response_model=userResponse)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Ottieni usere per email"""
    user = crud_user.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usere non trovato"
        )
    return user


@router.put("/users/{user_id}", response_model=userResponse)
def update_user(user_id: int, user_update: userUpdate, db: Session = Depends(get_db)):
    """
    Aggiorna usere
    
    - Aggiorna solo i campi forniti
    - Non può modificare la password (usa l'endpoint dedicato)
    """
    user = crud_user.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usere non trovato"
        )
    return user


@router.post("/users/{user_id}/change-password", response_model=userResponse)
def change_password(user_id: int, password_data: userChangePassword, db: Session = Depends(get_db)):
    """
    Cambia password del usere
    
    - Verifica la vecchia password
    - Imposta la nuova password
    """
    user = crud_user.change_password(
        db, 
        user_id, 
        password_data.old_password, 
        password_data.new_password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="usere non trovato o password non corretta"
        )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Elimina usere (soft delete)
    
    - Imposta active=False invece di eliminare il record
    """
    if not crud_user.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usere non trovato"
        )