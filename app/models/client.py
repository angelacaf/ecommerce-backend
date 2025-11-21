"""
Client model - rappresenta un cliente nel database
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    """
    Modello Client per la tabella clients nel database.
    
    Attributi:
        id: ID univoco del cliente
        email: Email del cliente (unique)
        password_hash: Password hashata
        first_name: Nome
        last_name: Cognome
        phone: Numero di telefono
        address: Indirizzo
        city: Città
        postal_code: CAP
        state: Provincia/Stato
        country: Nazione (default: Italy)
        active: Se l'account è attivo
        email_verified: Se l'email è verificata
        created_at: Data di registrazione
        updated_at: Data ultimo aggiornamento
    """
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(10), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(100), default="Italy", nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relazioni
    orders = relationship("Order", back_populates="client", cascade="all, delete-orphan")