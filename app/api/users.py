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
    User,
    UserPublic,
    UserLogin,
    UserChangePassword,
    TokenWithUser
)
from app.crud import user as crud_user
from app.utils.auth import create_access_token, verify_password, verify_token_with_details, ACCESS_TOKEN_EXPIRE_MINUTES  
from app.utils.dependencies import get_current_user, require_admin
from app.models.user import User as UserModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 

router = APIRouter()
security = HTTPBearer()

# ==================== REGISTRAZIONE & LOGIN ====================

@router.post("/users/register", response_model=TokenWithUser, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra nuovo utente e restituisce token JWT con dati pubblici
    """
    # Verifica se email già esistente
    existing_user = crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    # Crea utente nel database
    new_user = crud_user.create_user(db, user)
    
    # Crea token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),  # Standard OAuth2: subject
            "email": new_user.email,
            "role": new_user.role
        },
        expires_delta=access_token_expires
    )
    
    # Restituisce TokenWithUser (access_token + user pubblico)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user  # Pydantic converte a UserPublic automaticamente
    }


@router.post("/users/login", response_model=TokenWithUser)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login utente e restituisce token JWT con dati pubblici
    """
    # Cerca utente per email
    user = crud_user.get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verifica password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verifica account attivo
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disattivato"
        )
    
    # Crea token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # Standard OAuth2: subject
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    # Restituisce TokenWithUser (access_token + user pubblico)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user  # Pydantic converte a UserPublic automaticamente
    }



# ==================== VERIFICA TOKEN ====================

@router.get("/users/verify-token")
def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    """
    Verifica token JWT con dettagli completi su scadenza
    
    Headers richiesti:
        Authorization: Bearer <token>
    
    Returns:
        200: Token valido con dettagli utente e scadenza
        401: Token non valido o scaduto
    """
    
    # Il token è già estratto da HTTPBearer
    token = credentials.credentials
    
    # Verifica il token con dettagli
    result = verify_token_with_details(token)
    
    if not result['valid']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['error']
        )
    
    # Token valido, recupera info utente
    payload = result['payload']
    user_id = int(payload.get('sub'))
    user = crud_user.get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    return {
        "valid": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "active": user.active
        },
        "expires_in": result['expires_in'],
        "expires_at": result['expires_at'],
        "message": "Token valido"
    }

# ==================== PROFILO UTENTE ====================

@router.get("/users/me", response_model=User)
def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    """
    Ottieni profilo completo dell'utente autenticato
    """
    return current_user


@router.put("/users/me", response_model=User)
def update_my_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Aggiorna profilo dell'utente autenticato
    """
    updated_user = crud_user.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return updated_user


@router.post("/users/me/change-password", status_code=status.HTTP_200_OK)
def change_my_password(
    password_data: UserChangePassword,
    current_user: UserModel = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    """
    Cambia password dell'utente autenticato
    """
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
    return {"message": "Password aggiornata con successo"}


# ==================== ADMIN ENDPOINTS ====================

@router.get("/users", response_model=list[User])
def list_users(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    current_user: UserModel = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """
    Lista tutti gli utenti (SOLO ADMIN)
    """
    return crud_user.get_users(db, skip, limit, active_only)


@router.get("/users/email/{email}", response_model=User)
def get_user_by_email(
    email: str,
    current_user: UserModel = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """
    Ottieni utente per email (SOLO ADMIN)
    """
    user = crud_user.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return user


@router.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    current_user: UserModel = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """
    Dettaglio utente per ID (SOLO ADMIN)
    """
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
    current_user: UserModel = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """
    Elimina utente (SOLO ADMIN)
    """
    if not crud_user.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return None