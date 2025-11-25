"""
Dependencies for Authentication and Authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db_connection import get_db
from app.models.user import User, UserRole
from app.utils.auth import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Ottiene l'utente corrente dal token JWT
    
    Args:
        credentials: Token Bearer dall'header Authorization
        db: Sessione database
    
    Returns:
        Oggetto User del database
    
    Raises:
        HTTPException: Se token invalido, scaduto, o utente non trovato
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Estrae user_id dal campo "sub" (standard OAuth2)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido - subject mancante",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Converte in int
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID non valido nel token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Cerca utente nel database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verifica che l'account sia attivo
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disattivato"
        )
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica che l'utente corrente sia un amministratore
    
    Args:
        current_user: Utente corrente ottenuto da get_current_user
    
    Returns:
        Oggetto User se è admin
    
    Raises:
        HTTPException: Se l'utente non è admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato. Solo amministratori."
        )
    return current_user