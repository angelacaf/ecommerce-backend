"""
Payment utilities - Stripe integration
"""
import stripe
import os
from decimal import Decimal
from typing import Dict, Any

# Configura Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def create_checkout_session(
    order_id: int,
    order_number: str,
    amount: Decimal,
    items_count: int,
    success_url: str,
    cancel_url: str
) -> Dict[str, Any]:
    """
    Crea una Checkout Session Stripe
    
    Args:
        order_id: ID ordine nel database
        order_number: Numero ordine (es. ORD-20250127...)
        amount: Importo totale in euro
        items_count: Numero di prodotti nell'ordine
        success_url: URL di ritorno dopo pagamento riuscito
        cancel_url: URL di ritorno se utente annulla
    
    Returns:
        Dict con:
        - checkout_url: URL della pagina Stripe per il pagamento
        - session_id: ID della sessione Stripe
    
    Raises:
        stripe.error.StripeError: In caso di errore con Stripe
    """
    # Stripe usa centesimi
    amount_cents = int(amount * 100)
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Ordine {order_number}',
                        'description': f'{items_count} prodotti'
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=success_url + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_id}',
        cancel_url=cancel_url,
        metadata={
            'order_id': str(order_id),
            'order_number': order_number
        }
    )
    
    return {
        'checkout_url': checkout_session.url,
        'session_id': checkout_session.id
    }


def verify_payment(session_id: str) -> bool:
    """
    Verifica che il pagamento Stripe sia stato completato
    
    Args:
        session_id: ID della Checkout Session Stripe
    
    Returns:
        True se pagato, False altrimenti
    
    Raises:
        stripe.error.StripeError: In caso di errore con Stripe
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status == 'paid'


def get_payment_details(session_id: str) -> Dict[str, Any]:
    """
    Recupera dettagli completi del pagamento
    
    Args:
        session_id: ID della Checkout Session Stripe
    
    Returns:
        Dict con dettagli del pagamento:
        - payment_status: 'paid', 'unpaid', 'no_payment_required'
        - amount_total: Importo pagato (in centesimi)
        - currency: Valuta (es. 'eur')
        - customer_email: Email del cliente
        - payment_intent: ID del PaymentIntent
    
    Raises:
        stripe.error.StripeError: In caso di errore con Stripe
    """
    session = stripe.checkout.Session.retrieve(session_id)
    
    return {
        'payment_status': session.payment_status,
        'amount_total': session.amount_total,
        'currency': session.currency,
        'customer_email': session.customer_details.email if session.customer_details else None,
        'payment_intent': session.payment_intent
    }