"""
Payment utilities - Stripe Checkout (versione semplice)
"""
import stripe
import os
from decimal import Decimal

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def create_checkout_session(
    order_id: int,
    order_number: str,
    amount: Decimal,
    success_url: str,
    cancel_url: str
):
    """
    Crea una Checkout Session Stripe (reindirizza a pagina Stripe)
    
    Args:
        order_id: ID ordine
        order_number: Numero ordine
        amount: Importo in euro
        success_url: URL di ritorno dopo successo
        cancel_url: URL di ritorno dopo cancellazione
    
    Returns:
        URL della pagina Stripe
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
                        'description': 'Acquisto e-commerce'
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


def verify_checkout_session(session_id: str):
    """
    Verifica che la Checkout Session sia stata pagata
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status == 'paid'