"""
Order models - rappresentano ordini e dettagli ordini nel database
"""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    """
    Modello Order per la tabella orders nel database.
    
    Attributi:
        id: ID univoco dell'ordine
        client_id: ID del cliente (FK)
        order_number: Numero ordine univoco
        status: Stato ordine (pending, paid, processing, shipped, delivered, cancelled, refunded)
        total: Totale ordine
        subtotal: Subtotale (senza spese)
        shipping_cost: Costo spedizione
        tax: Tasse
        discount: Sconto applicato
        discount_code: Codice sconto usato
        shipping_address: Indirizzo spedizione
        shipping_city: Città spedizione
        shipping_postal_code: CAP spedizione
        shipping_state: Provincia/Stato spedizione
        shipping_country: Nazione spedizione
        notes: Note ordine
        payment_intent_id: ID transazione pagamento
        paid: Se l'ordine è stato pagato
        paid_at: Data pagamento
        shipped_at: Data spedizione
        delivered_at: Data consegna
        created_at: Data creazione
        updated_at: Data ultimo aggiornamento
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    status = Column(
        String(50), 
        nullable=False, 
        default="pending",
        index=True
    )
    
    # Prezzi
    total = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=Decimal("0.00"))
    tax = Column(Numeric(10, 2), default=Decimal("0.00"))
    discount = Column(Numeric(10, 2), default=Decimal("0.00"))
    discount_code = Column(String(50), nullable=True)
    
    # Indirizzo spedizione
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=True)
    shipping_postal_code = Column(String(10), nullable=True)
    shipping_state = Column(String(50), nullable=True)
    shipping_country = Column(String(100), default="Italy")
    
    # Info aggiuntive
    notes = Column(Text, nullable=True)
    payment_intent_id = Column(String(255), nullable=True)
    
    # Stati e date
    paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total >= 0', name='orders_total_check'),
        CheckConstraint('subtotal >= 0', name='orders_subtotal_check'),
        CheckConstraint('shipping_cost >= 0', name='orders_shipping_cost_check'),
        CheckConstraint('tax >= 0', name='orders_tax_check'),
        CheckConstraint('discount >= 0', name='orders_discount_check'),
        CheckConstraint(
            "status IN ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')",
            name='orders_status_check'
        ),
    )
    
    # Relazioni
    client = relationship("Client", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")


class OrderDetail(Base):
    """
    Modello OrderDetail per la tabella order_details nel database.
    
    Attributi:
        id: ID univoco del dettaglio
        order_id: ID dell'ordine (FK)
        product_id: ID del prodotto (FK)
        quantity: Quantità ordinata
        unit_price: Prezzo unitario al momento dell'ordine
        subtotal: Subtotale (quantity * unit_price)
    """
    __tablename__ = "order_details"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='order_details_quantity_check'),
        CheckConstraint('unit_price >= 0', name='order_details_unit_price_check'),
        CheckConstraint('subtotal >= 0', name='order_details_subtotal_check'),
    )
    
    # Relazioni
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")