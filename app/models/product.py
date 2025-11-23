"""
Product model - rappresenta un prodotto nel database
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

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
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False, index=True)  
    available_quantity = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500), nullable=True)
    sku = Column(String(100), nullable=True, unique=True, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True) 
    featured = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='products_price_check'),
        CheckConstraint('available_quantity >= 0', name='products_available_quantity_check'),
        {'schema': 'ecommerce'}
    )
    # Relazione con Category
    category_id = Column(Integer, ForeignKey('ecommerce.categories.id', ondelete='SET NULL'), nullable=True, index=True)
    category = relationship("Category", back_populates="products")

    # Relazione con OrderDetail
    order_details = relationship("OrderDetail", back_populates="product")