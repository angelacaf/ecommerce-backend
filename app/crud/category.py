"""
CRUD operations for Product model
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from decimal import Decimal

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


def get_products(
    db: Session,
    category_id: Optional[int] = None,
    active_only: bool = True,
    featured_only: bool = False,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Product]:
    """
    Get products with multiple filters
    
    Args:
        db: Database session
        category_id: Filter by category ID
        active_only: Show only active products
        featured_only: Show only featured products
        min_price: Minimum price filter
        max_price: Maximum price filter
        search: Search in name and description
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        List of products matching the filters
    """
    query = db.query(Product)
    
    # Filter by category
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Filter active products
    if active_only:
        query = query.filter(Product.active == True)
    
    # Filter featured products
    if featured_only:
        query = query.filter(Product.featured == True)
    
    # Filter by price range
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Search in name and description
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) |
            (Product.description.ilike(search_filter))
        )
    
    # Apply pagination and return
    return query.order_by(Product.name).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Get product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Get product by SKU"""
    return db.query(Product).filter(Product.sku == sku).first()


def get_products_with_category(
    db: Session,
    category_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50
) -> List[Product]:
    """Get products with category details loaded (eager loading)"""
    query = db.query(Product).options(joinedload(Product.category))
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if active_only:
        query = query.filter(Product.active == True)
    
    return query.order_by(Product.name).offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    """Create new product"""
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        available_quantity=product.available_quantity,
        image_url=product.image_url,
        sku=product.sku,
        active=product.active,
        featured=product.featured,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session,
    product_id: int,
    product_update: ProductUpdate
) -> Optional[Product]:
    """Update existing product"""
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return None
    
    # Update only provided fields
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """Soft delete product (set active=False)"""
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return False
    
    db_product.active = False
    db.commit()
    return True


def hard_delete_product(db: Session, product_id: int) -> bool:
    """Hard delete product (permanent deletion)"""
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True


def count_products(
    db: Session,
    category_id: Optional[int] = None,
    active_only: bool = True
) -> int:
    """Count total products matching filters"""
    query = db.query(Product)
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if active_only:
        query = query.filter(Product.active == True)
    
    return query.count()


def update_stock(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
    """
    Update product stock quantity
    
    Args:
        product_id: Product ID
        quantity_change: Amount to add (positive) or subtract (negative)
    
    Returns:
        Updated product or None if not found or insufficient stock
    """
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return None
    
    new_quantity = db_product.available_quantity + quantity_change
    
    # Prevent negative stock
    if new_quantity < 0:
        return None
    
    db_product.available_quantity = new_quantity
    db.commit()
    db.refresh(db_product)
    return db_product