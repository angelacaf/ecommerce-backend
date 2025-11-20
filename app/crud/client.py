"""
CRUD operations per Client
"""
from typing import Optional
from sqlalchemy.orm import Session
import bcrypt

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


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

def get_client(db: Session, client_id: int) -> Optional[Client]:
    """Ottieni un cliente per ID"""
    return db.query(Client).filter(Client.id == client_id).first()


def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    """Ottieni un cliente per email"""
    return db.query(Client).filter(Client.email == email).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> list[Client]:
    """Ottieni lista clienti"""
    query = db.query(Client)
    if active_only:
        query = query.filter(Client.active == True)
    return query.offset(skip).limit(limit).all()


# ==================== CREA ====================

def create_client(db: Session, client: ClientCreate) -> Client:
    """Registra nuovo cliente"""
    # Hash password
    hashed_password = hash_password(client.password)
    
    # Crea client senza il campo password
    client_data = client.model_dump(exclude={'password'})
    db_client = Client(**client_data, password_hash=hashed_password)
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# ==================== AGGIORNA ====================

def update_client(db: Session, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    """Aggiorna cliente"""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    # Aggiorna solo i campi forniti
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


def change_password(db: Session, client_id: int, old_password: str, new_password: str) -> Optional[Client]:
    """Cambia password del cliente"""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    # Verifica vecchia password
    if not verify_password(old_password, db_client.password_hash):
        return None
    
    # Aggiorna con nuova password
    db_client.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(db_client)
    return db_client


# ==================== ELIMINA ====================

def delete_client(db: Session, client_id: int) -> bool:
    """Elimina cliente (soft delete - imposta active=False)"""
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db_client.active = False
    db.commit()
    return True


# ==================== AUTENTICAZIONE ====================

def authenticate_client(db: Session, email: str, password: str) -> Optional[Client]:
    """Autentica cliente con email e password"""
    client = get_client_by_email(db, email)
    if not client:
        return None
    if not verify_password(password, client.password_hash):
        return None
    if not client.active:
        return None
    return client