"""
CRUD operations per User
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password


# ==================== LEGGI ====================

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Ottieni un utente per ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Ottieni un utente per email"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> list[User]:
    """Ottieni lista utenti"""
    query = db.query(User)
    if active_only:
        query = query.filter(User.active == True)
    return query.offset(skip).limit(limit).all()


# ==================== CREA ====================

def create_user(db: Session, user: UserCreate) -> User:
    """Registra nuovo utente"""
    # Hash password usando auth.py
    hashed_password = get_password_hash(user.password)
    
    # Crea User senza il campo password
    user_data = user.model_dump(exclude={'password'})
    db_user = User(**user_data, password_hash=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== AGGIORNA ====================

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Aggiorna utente"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Aggiorna solo i campi forniti
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> Optional[User]:
    """Cambia password dell'utente"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Verifica vecchia password
    if not verify_password(old_password, db_user.password_hash):
        return None
    
    # Aggiorna con nuova password
    db_user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== ELIMINA ====================

def delete_user(db: Session, user_id: int) -> bool:
    """Elimina utente (soft delete - imposta active=False)"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.active = False
    db.commit()
    return True


# ==================== AUTENTICAZIONE ====================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Autentica utente con email e password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.active:
        return None
    return user