"""
Order schemas - Pydantic models per validazione e serializzazione ordini
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============== ORDER ITEM (dettagli ordine) ==============
class OrderItemCreate(BaseModel):
    """Schema per creare un item dell'ordine nel carrello"""
    product_id: int = Field(..., gt=0, description="ID del prodotto")
    quantity: int = Field(..., gt=0, description="Quantità da ordinare")


class OrderItemResponse(BaseModel):
    """Schema per la risposta di un item dell'ordine"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    
    class Config:
        from_attributes = True


# ============== ORDER (ordine completo) ==============
class OrderCreate(BaseModel):
    """
    Schema per creare un nuovo ordine MINIMALE (solo prodotti)
    I metadati di spedizione vengono aggiunti in fase di pagamento
    """
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Prodotti nel carrello")
    discount_code: Optional[str] = Field(None, max_length=50)

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        """Valida che ci sia almeno un prodotto"""
        if not v or len(v) == 0:
            raise ValueError('Order must contain at least one item')
        return v


class OrderResponse(BaseModel):
    """Schema per la risposta completa di un ordine"""
    id: int
    order_number: str
    user_id: int
    status: str
    total: Decimal
    subtotal: Decimal
    shipping_cost: Decimal
    tax: Decimal
    discount: Decimal
    discount_code: Optional[str]
    shipping_address: Optional[str]
    shipping_city: Optional[str]
    shipping_postal_code: Optional[str]
    shipping_state: Optional[str]
    shipping_country: Optional[str]
    notes: Optional[str]
    paid: bool
    paid_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema per lista ordini (senza dettagli prodotti per performance)"""
    id: int
    order_number: str
    status: str
    total: Decimal
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema per aggiornare lo stato di un ordine (admin)"""
    status: str = Field(
        ..., 
        pattern="^(pending|paid|processing|shipped|delivered|cancelled|refunded)$",
        description="Nuovo stato dell'ordine"
    )


# ============== PAYMENT SCHEMAS ==============
class PaymentInitiate(BaseModel):
    """
    Schema per iniziare il pagamento
    Include i metadati dell'ordine che vengono salvati PRIMA di andare su Stripe
    """
    # Metadati di spedizione (AGGIUNTI QUI)
    shipping_address: str = Field(..., min_length=5, description="Indirizzo di spedizione")
    shipping_city: str = Field(..., min_length=2)
    shipping_postal_code: str = Field(..., min_length=5, max_length=10)
    shipping_state: Optional[str] = None
    shipping_country: str = Field(default="Italy")
    notes: Optional[str] = Field(None, max_length=500)
    
    # URL di ritorno da Stripe
    success_url: str = "http://localhost:3000/payment-success"
    cancel_url: str = "http://localhost:3000/payment-cancel"


class PaymentConfirmation(BaseModel):
    """Schema per confermare il pagamento dopo ritorno da Stripe"""
    session_id: str

