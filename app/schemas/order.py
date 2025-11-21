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
        from_attributes = True  # Per convertire da SQLAlchemy a Pydantic


# ============== ORDER (ordine completo) ==============
class OrderCreate(BaseModel):
    """Schema per creare un nuovo ordine (checkout)"""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Prodotti nel carrello")
    shipping_address: str = Field(..., min_length=5, description="Indirizzo di spedizione")
    shipping_city: str = Field(..., min_length=2)
    shipping_postal_code: str = Field(..., min_length=5, max_length=10)
    shipping_state: Optional[str] = None
    shipping_country: str = Field(default="Italy")
    notes: Optional[str] = Field(None, max_length=500)
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
    client_id: int
    status: str
    total: Decimal
    subtotal: Decimal
    shipping_cost: Decimal
    tax: Decimal
    discount: Decimal
    discount_code: Optional[str]
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_state: Optional[str]
    shipping_country: str
    notes: Optional[str]
    paid: bool
    paid_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []  # Lista prodotti nell'ordine
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema per lista ordini (senza dettagli prodotti per performance)"""
    id: int
    order_number: str
    status: str
    total: Decimal
    created_at: datetime
    items_count: int  # Numero di prodotti
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema per aggiornare lo stato di un ordine (admin)"""
    status: str = Field(
        ..., 
        pattern="^(pending|paid|processing|shipped|delivered|cancelled|refunded)$",
        description="Nuovo stato dell'ordine"
    )


# ============== EXAMPLE PAYLOADS ==============
class OrderCreateExample:
    """Esempio di payload per creare un ordine"""
    example = {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ],
        "shipping_address": "Via Roma 123",
        "shipping_city": "Rome",
        "shipping_postal_code": "00100",
        "shipping_state": "RM",
        "shipping_country": "Italy",
        "notes": "Suonare il campanello",
        "discount_code": "SUMMER2024"
    }