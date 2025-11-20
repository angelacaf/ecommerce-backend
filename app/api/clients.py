"""
Clients API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.client import (
    ClientCreate, 
    ClientUpdate, 
    ClientResponse, 
    ClientLogin,
    ClientChangePassword
)
from app.crud import client as crud_client

# Crea router per clients
router = APIRouter()


# ==================== REGISTRAZIONE & LOGIN ====================

@router.post("/clients/register", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def register_client(client: ClientCreate, db: Session = Depends(get_db)):
    """
    Registra un nuovo cliente
    
    - Verifica che l'email non sia già registrata
    - Hash della password
    - Crea il nuovo cliente
    """
    # Verifica se email già esiste
    existing_client = crud_client.get_client_by_email(db, client.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    return crud_client.create_client(db, client)


@router.post("/clients/login", response_model=ClientResponse)
def login_client(credentials: ClientLogin, db: Session = Depends(get_db)):
    """
    Login cliente
    
    - Verifica email e password
    - Restituisce i dati del cliente (in produzione restituirebbe un JWT token)
    """
    client = crud_client.authenticate_client(db, credentials.email, credentials.password)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti"
        )
    
    return client


# ==================== CRUD CLIENTS ====================

@router.get("/clients", response_model=list[ClientResponse])
def list_clients(skip: int = 0, limit: int = 20, active_only: bool = True, db: Session = Depends(get_db)):
    """
    Lista clienti
    
    - skip: numero di record da saltare (per paginazione)
    - limit: numero massimo di record da restituire
    - active_only: se True, restituisce solo clienti attivi
    """
    return crud_client.get_clients(db, skip, limit, active_only)


@router.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Dettaglio cliente"""
    client = crud_client.get_client(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    return client


@router.get("/clients/email/{email}", response_model=ClientResponse)
def get_client_by_email(email: str, db: Session = Depends(get_db)):
    """Ottieni cliente per email"""
    client = crud_client.get_client_by_email(db, email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    return client


@router.put("/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """
    Aggiorna cliente
    
    - Aggiorna solo i campi forniti
    - Non può modificare la password (usa l'endpoint dedicato)
    """
    client = crud_client.update_client(db, client_id, client_update)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    return client


@router.post("/clients/{client_id}/change-password", response_model=ClientResponse)
def change_password(client_id: int, password_data: ClientChangePassword, db: Session = Depends(get_db)):
    """
    Cambia password del cliente
    
    - Verifica la vecchia password
    - Imposta la nuova password
    """
    client = crud_client.change_password(
        db, 
        client_id, 
        password_data.old_password, 
        password_data.new_password
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente non trovato o password non corretta"
        )
    return client


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """
    Elimina cliente (soft delete)
    
    - Imposta active=False invece di eliminare il record
    """
    if not crud_client.delete_client(db, client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )