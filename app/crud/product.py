"""
CRUD operations per Product
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


# ==================== LEGGI ====================

def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Ottieni un prodotto per ID"""
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    """Ottieni lista prodotti"""
    return db.query(Product).filter(Product.active == True).offset(skip).limit(limit).all()


# ==================== CREA ====================

def create_product(db: Session, product: ProductCreate) -> Product:
    """Crea nuovo prodotto"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# ==================== AGGIORNA ====================

def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Aggiorna prodotto"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    # Aggiorna solo i campi forniti
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


# ==================== ELIMINA ====================

def delete_product(db: Session, product_id: int) -> bool:
    """Elimina prodotto (soft delete - imposta active=False)"""
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db_product.active = False
    db.commit()
    return True