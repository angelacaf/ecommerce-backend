"""
Orders router - Gestione ordini e-commerce
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone
from decimal import Decimal
import stripe
import os

from app.db_connection import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderDetail
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderItemResponse,
    OrderStatusUpdate,
    PaymentInitiate,
    PaymentConfirmation
)
from app.utils.dependencies import get_current_user, require_admin

# ==================== CONFIGURAZIONE ====================

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# ==================== UTILITY FUNCTIONS ====================

def generate_order_number() -> str:
    """Genera un numero ordine univoco basato su timestamp"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}"


def calculate_order_totals(subtotal: Decimal) -> dict:
    """
    Calcola i totali dell'ordine (spedizione, tasse, sconti)
    
    Args:
        subtotal: Subtotale dei prodotti
    
    Returns:
        Dict con shipping_cost, tax, discount, total
    """
    shipping_cost = Decimal("5.00") if subtotal < Decimal("50.00") else Decimal("0.00")
    tax = Decimal("0.00")
    discount = Decimal("0.00")
    total = subtotal + shipping_cost + tax - discount
    
    return {
        "shipping_cost": shipping_cost,
        "tax": tax,
        "discount": discount,
        "total": total
    }


def validate_product_availability(product: Product, quantity: int) -> None:
    """
    Valida disponibilità prodotto
    
    Args:
        product: Prodotto da validare
        quantity: Quantità richiesta
    
    Raises:
        HTTPException: Se prodotto non disponibile
    """
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{product.name}' is not available"
        )
    
    if product.available_quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock for '{product.name}'. Available: {product.available_quantity}, Requested: {quantity}"
        )


def build_order_response(order: Order) -> OrderResponse:
    """
    Costruisce la risposta OrderResponse da un oggetto Order
    
    Args:
        order: Oggetto Order con order_details caricati
    
    Returns:
        OrderResponse con tutti i dati
    """
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
        user_id=order.user_id,
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


# ==================== ENDPOINTS UTENTE ====================

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo ordine in stato 'pending'
    
    Best Practice:
    - NON decrementa l'inventario (lo farà solo dopo pagamento)
    - Verifica disponibilità prodotti
    - Calcola prezzi
    - I metadati (indirizzo) vengono aggiunti in fase di pagamento
    """
    # Verifica che ci siano prodotti
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    # Verifica disponibilità e calcola subtotale
    subtotal = Decimal("0.00")
    order_items = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        validate_product_availability(product, item.quantity)
        
        item_price = Decimal(str(product.price))
        item_subtotal = item_price * item.quantity
        subtotal += item_subtotal
        
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": item_price,
            "subtotal": item_subtotal
        })
    
    # Calcola totali
    totals = calculate_order_totals(subtotal)
    
    # Crea ordine pending (senza metadati di spedizione)
    new_order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        status="pending",
        subtotal=subtotal,
        shipping_cost=totals["shipping_cost"],
        tax=totals["tax"],
        discount=totals["discount"],
        discount_code=order_data.discount_code,
        total=totals["total"],
        paid=False
    )
    
    db.add(new_order)
    db.flush()
    
    # Crea dettagli ordine (senza decrementare inventario)
    for item_data in order_items:
        order_detail = OrderDetail(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            subtotal=item_data["subtotal"]
        )
        db.add(order_detail)
    
    db.commit()
    
    # Carica relazioni e costruisci risposta
    order_with_details = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == new_order.id).first()
    
    return build_order_response(order_with_details)


@router.get("/", response_model=List[OrderListResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recupera tutti gli ordini dell'utente autenticato"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return [
        OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
            items_count=len(order.order_details)
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recupera dettagli di un ordine specifico"""
    order = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return build_order_response(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancella un ordine in stato 'pending'
    
    Best Practice: Non serve ripristinare l'inventario
    perché non è mai stato decrementato
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
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
    
    db.delete(order)
    db.commit()
    
    return None

@router.post("/{order_id}/initiate-payment")
def initiate_payment(
    order_id: int,
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Avvia il processo di pagamento Stripe"""
    
    # Carica ordine con dettagli E prodotti
    order = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order already paid or cancelled")
    
    # Verifica disponibilità prodotti
    for detail in order.order_details:
        product = db.query(Product).filter(Product.id == detail.product_id).first()
        validate_product_availability(product, detail.quantity)
    
    # Salva metadati di spedizione
    order.shipping_address = payment_data.shipping_address
    order.shipping_city = payment_data.shipping_city
    order.shipping_postal_code = payment_data.shipping_postal_code
    order.shipping_state = payment_data.shipping_state
    order.shipping_country = payment_data.shipping_country
    order.notes = payment_data.notes
    
    db.commit()
    db.refresh(order)  # Ricarica l'ordine aggiornato
    
    # Crea line items
    line_items = []
    
    for detail in order.order_details:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': detail.product.name,
                    'description': f'SKU: {detail.product.sku}' if detail.product.sku else None,
                },
                'unit_amount': int(detail.unit_price * 100),
            },
            'quantity': detail.quantity,
        })
    
    if order.shipping_cost > 0:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': 'Spedizione',
                    'description': 'Costo di spedizione'
                },
                'unit_amount': int(order.shipping_cost * 100),
            },
            'quantity': 1,
        })
    
    # Crea Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=payment_data.success_url + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
            cancel_url=payment_data.cancel_url,
            metadata={
                'order_id': str(order.id),
                'order_number': order.order_number
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "order_id": order.id,
            "order_number": order.order_number,
            "total": float(order.total),
            "shipping_info": {
                "address": order.shipping_address,
                "city": order.shipping_city,
                "postal_code": order.shipping_postal_code,
                "state": order.shipping_state,
                "country": order.shipping_country,
                "notes": order.notes
            }
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )

    
@router.post("/{order_id}/confirm-payment")
def confirm_payment(
    order_id: int,
    confirmation: PaymentConfirmation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conferma il pagamento dopo ritorno da Stripe
    
    Best Practice: SOLO ORA decrementa l'inventario
    """
    # Carica ordine con dettagli
    order = db.query(Order).options(
        joinedload(Order.order_details)
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "pending":
        return {
            "message": "Order already confirmed",
            "status": order.status
        }
    
    # Verifica pagamento con Stripe
    try:
        session = stripe.checkout.Session.retrieve(confirmation.session_id)
        
        if session.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed"
            )
        
        # Decrementa inventario (SOLO DOPO PAGAMENTO)
        for detail in order.order_details:
            product = db.query(Product).filter(Product.id == detail.product_id).first()
            
            if product:
                product.available_quantity -= detail.quantity
        
        # Aggiorna ordine a PAID
        order.status = "paid"
        order.paid = True
        order.paid_at = datetime.now(timezone.utc)
        order.payment_intent_id = confirmation.session_id
        
        db.commit()
        
        return {
            "message": "Payment confirmed",
            "order_id": order.id,
            "order_number": order.order_number,
            "status": "paid"
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


# ==================== ENDPOINTS ADMIN ====================

@router.get("/admin/all", response_model=List[OrderListResponse])
def get_all_orders_admin(
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Recupera tutti gli ordini di tutti gli utenti (ADMIN)"""
    orders = db.query(Order).order_by(
        Order.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
            items_count=len(order.order_details)
        )
        for order in orders
    ]


@router.get("/admin/{user_id}/orders", response_model=List[OrderListResponse])
def get_user_orders_admin(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Recupera tutti gli ordini di un utente specifico (ADMIN)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).all()
    
    return [
        OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
            items_count=len(order.order_details)
        )
        for order in orders
    ]


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna lo stato di un ordine (ADMIN)"""
    order = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Aggiorna status
    order.status = status_update.status
    
    # Aggiorna timestamp in base allo status
    if status_update.status == "paid" and not order.paid:
        order.paid = True
        order.paid_at = datetime.now(timezone.utc)
    elif status_update.status == "shipped":
        order.shipped_at = datetime.now(timezone.utc)
    elif status_update.status == "delivered":
        order.delivered_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(order)
    
    return build_order_response(order)