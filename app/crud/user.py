"""
CRUD operations per user
"""
from typing import Optional
from sqlalchemy.orm import Session
import bcrypt

from app.models.user import User
from app.schemas.user import userCreate, userUpdate


# ==================== UTILITY ====================

def hash_password(password: str) -> str:
    """Hash della password usando bcrypt direttamente"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password usando bcrypt direttamente"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ==================== LEGGI ====================

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Ottieni un usere per ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Ottieni un usere per email"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> list[User]:
    """Ottieni lista useri"""
    query = db.query(User)
    if active_only:
        query = query.filter(User.active == True)
    return query.offset(skip).limit(limit).all()


# ==================== CREA ====================

def create_user(db: Session, user: userCreate) -> User:
    """Registra nuovo usere"""
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Crea user senza il campo password
    user_data = user.model_dump(exclude={'password'})
    db_user = user(**user_data, password_hash=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== AGGIORNA ====================

def update_user(db: Session, user_id: int, user_update: userUpdate) -> Optional[User]:
    """Aggiorna usere"""
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
    """Cambia password del usere"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Verifica vecchia password
    if not verify_password(old_password, db_user.password_hash):
        return None
    
    # Aggiorna con nuova password
    db_user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== ELIMINA ====================

def delete_user(db: Session, user_id: int) -> bool:
    """Elimina usere (soft delete - imposta active=False)"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.active = False
    db.commit()
    return True


# ==================== AUTENTICAZIONE ====================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Autentica usere con email e password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.active:
        return None
    return user