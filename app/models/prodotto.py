from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Prodotto(Base):
    """Model per tabella prodotti"""
    
    # Nome tabella nel database  METADATA (configurazione)
    __tablename__ = "prodotti"
    
    # Colonne (come nella tabella PostgreSQL) COLUMN DESCRIPTORS (mappano colonne SQL)
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descrizione = Column(Text)
    prezzo = Column(Numeric(10, 2), nullable=False)
    quantita_disponibile = Column(Integer, nullable=False, default=0)
    immagine_url = Column(String(500))
    sku = Column(String(100), unique=True)
    attivo = Column(Boolean, default=True)
    in_evidenza = Column(Boolean, default=False)
    creato_il = Column(DateTime(timezone=True), server_default=func.now())
    aggiornato_il = Column(DateTime(timezone=True), onupdate=func.now())