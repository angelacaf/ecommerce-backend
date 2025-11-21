"""
Orders router - Gestione ordini
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone
from decimal import Decimal

from app.database import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.order import Order, OrderDetail
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderItemResponse,
    OrderStatusUpdate
)

router = APIRouter(
    prefix="/orders",
    # tags=["orders"]
)

# Client ID fisso per testing
TEMP_CLIENT_ID = 1


def generate_order_number() -> str:
    """Genera un numero ordine univoco"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo ordine per il cliente con ID=1
    
    - Verifica disponibilità prodotti
    - Calcola prezzi
    - Crea ordine e dettagli
    - Aggiorna quantità disponibili
    """
    
    # Verifica che il cliente esista
    client = db.query(Client).filter(Client.id == TEMP_CLIENT_ID).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {TEMP_CLIENT_ID} not found"
        )
    
    # 1. Verifica che ci siano prodotti
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    # 2. Verifica disponibilità prodotti e calcola subtotale
    subtotal = Decimal("0.00")
    order_items = []
    
    for item in order_data.items:
        # Recupera prodotto
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found"
            )
        
        if not product.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not available"
            )
        
        if product.available_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product '{product.name}'. Available: {product.available_quantity}, Requested: {item.quantity}"
            )
        
        # Calcola subtotale item
        item_price = Decimal(str(product.price))
        item_subtotal = item_price * item.quantity
        subtotal += item_subtotal
        
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": item_price,
            "subtotal": item_subtotal
        })
    
    # 3. Calcola costi aggiuntivi
    shipping_cost = Decimal("5.00") if subtotal < Decimal("50.00") else Decimal("0.00")
    tax = Decimal("0.00")
    discount = Decimal("0.00")
    
    total = subtotal + shipping_cost + tax - discount
    
    # 4. Crea ordine  
    new_order = Order(                  
        client_id=TEMP_CLIENT_ID,
        order_number=generate_order_number(),
        status="pending",
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax=tax,
        discount=discount,
        discount_code=order_data.discount_code,
        total=total,
        shipping_address=order_data.shipping_address,
        shipping_city=order_data.shipping_city,
        shipping_postal_code=order_data.shipping_postal_code,
        shipping_state=order_data.shipping_state,
        shipping_country=order_data.shipping_country,
        notes=order_data.notes,
        paid=False
    ) # Crea oggetto in memoria
    
    db.add(new_order)   # Aggiungi alla sessione
    db.flush()          # Invia al DB per generare l'ID
    

    # 5. Crea dettagli ordine e aggiorna quantità
    for item_data in order_items:
        order_detail = OrderDetail(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            subtotal=item_data["subtotal"]
        )
        db.add(order_detail)
        
        # Aggiorna quantità disponibile prodotto
        item_data["product"].available_quantity -= item_data["quantity"]
    
    db.commit()                 # Salva tutto definitivamente
    db.refresh(new_order)       # Ricarica
    
    # 6. Carica relazioni per la risposta , carica i dettagli dell'ordine e i prodotti
    order_with_details = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == new_order.id).first()
    
    # 7. Costruisci risposta
    response_items = [
        OrderItemResponse(
            id=detail.id,
            product_id=detail.product_id,
            product_name=detail.product.name,
            quantity=detail.quantity,
            unit_price=detail.unit_price,
            subtotal=detail.subtotal
        )
        for detail in order_with_details.order_details
    ]
    
    return OrderResponse(
        id=order_with_details.id,
        order_number=order_with_details.order_number,
        client_id=order_with_details.client_id,
        status=order_with_details.status,
        total=order_with_details.total,
        subtotal=order_with_details.subtotal,
        shipping_cost=order_with_details.shipping_cost,
        tax=order_with_details.tax,
        discount=order_with_details.discount,
        discount_code=order_with_details.discount_code,
        shipping_address=order_with_details.shipping_address,
        shipping_city=order_with_details.shipping_city,
        shipping_postal_code=order_with_details.shipping_postal_code,
        shipping_state=order_with_details.shipping_state,
        shipping_country=order_with_details.shipping_country,
        notes=order_with_details.notes,
        paid=order_with_details.paid,
        paid_at=order_with_details.paid_at,
        shipped_at=order_with_details.shipped_at,
        delivered_at=order_with_details.delivered_at,
        created_at=order_with_details.created_at,
        updated_at=order_with_details.updated_at,
        items=response_items
    )


@router.get("/", response_model=List[OrderListResponse])
def get_all_orders(db: Session = Depends(get_db)):
    """
    Recupera tutti gli ordini del cliente ID=1
    """
    orders = db.query(Order).filter(
        Order.client_id == TEMP_CLIENT_ID
    ).order_by(Order.created_at.desc()).all()
    
    response = []
    for order in orders:
        items_count = db.query(OrderDetail).filter(OrderDetail.order_id == order.id).count()
        response.append(
            OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                total=order.total,
                created_at=order.created_at,
                items_count=items_count
            )
        )
    
    return response


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    """
    Recupera dettagli di un ordine specifico
    """
    order = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    response_items = [
        OrderItemResponse(
            id=detail.id,
            product_id=detail.product_id,
            product_name=detail.product.name,
            quantity=detail.quantity,
            unit_price=detail.unit_price,
            subtotal=detail.subtotal
        )
        for detail in order.order_details
    ]
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        client_id=order.client_id,
        status=order.status,
        total=order.total,
        subtotal=order.subtotal,
        shipping_cost=order.shipping_cost,
        tax=order.tax,
        discount=order.discount,
        discount_code=order.discount_code,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_postal_code=order.shipping_postal_code,
        shipping_state=order.shipping_state,
        shipping_country=order.shipping_country,
        notes=order.notes,
        paid=order.paid,
        paid_at=order.paid_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=response_items
    )


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Aggiorna lo stato di un ordine
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = status_update.status
    
    if status_update.status == "paid" and not order.paid:
        order.paid = True
        order.paid_at = datetime.now(timezone.utc)
    elif status_update.status == "shipped":
        order.shipped_at = datetime.now(timezone.utc)
    elif status_update.status == "delivered":
        order.delivered_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(order)
    
    order_with_details = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == order.id).first()
    
    response_items = [
        OrderItemResponse(
            id=detail.id,
            product_id=detail.product_id,
            product_name=detail.product.name,
            quantity=detail.quantity,
            unit_price=detail.unit_price,
            subtotal=detail.subtotal
        )
        for detail in order_with_details.order_details
    ]
    
    return OrderResponse(
        id=order_with_details.id,
        order_number=order_with_details.order_number,
        client_id=order_with_details.client_id,
        status=order_with_details.status,
        total=order_with_details.total,
        subtotal=order_with_details.subtotal,
        shipping_cost=order_with_details.shipping_cost,
        tax=order_with_details.tax,
        discount=order_with_details.discount,
        discount_code=order_with_details.discount_code,
        shipping_address=order_with_details.shipping_address,
        shipping_city=order_with_details.shipping_city,
        shipping_postal_code=order_with_details.shipping_postal_code,
        shipping_state=order_with_details.shipping_state,
        shipping_country=order_with_details.shipping_country,
        notes=order_with_details.notes,
        paid=order_with_details.paid,
        paid_at=order_with_details.paid_at,
        shipped_at=order_with_details.shipped_at,
        delivered_at=order_with_details.delivered_at,
        created_at=order_with_details.created_at,
        updated_at=order_with_details.updated_at,
        items=response_items
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancella un ordine (solo se pending)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled"
        )
    
    # Ripristina quantità prodotti
    order_details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
    for detail in order_details:
        product = db.query(Product).filter(Product.id == detail.product_id).first()
        if product:
            product.available_quantity += detail.quantity
    
    db.delete(order)
    db.commit()
    
    return None