"""
Product model - rappresenta un prodotto nel database
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text

from app.database import Base


class Product(Base):
    """
    Modello Product per la tabella products nel database.
    
    Attributi:
        id: ID univoco del prodotto
        name: Nome del prodotto
        description: Descrizione dettagliata
        price: Prezzo del prodotto
        available_quantity: Quantità disponibile in magazzino
        image_url: URL dell'immagine del prodotto
        sku: Codice SKU del prodotto
        active: Se il prodotto è attivo/visibile
        featured: Se il prodotto è in evidenza
        created_at: Data di creazione
        updated_at: Data ultimo aggiornamento
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500), nullable=True)
    sku = Column(String(100), nullable=True, unique=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
