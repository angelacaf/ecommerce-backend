"""
CRUD operations for Category model
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category


def get_categories(db: Session, active_only: bool = True) -> List[Category]:
    """Get all categories"""
    query = db.query(Category)
    
    if active_only:
        query = query.filter(Category.active == True)
    
    return query.order_by(Category.name).all()


def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Get category by exact name (case insensitive)"""
    return db.query(Category).filter(Category.name.ilike(name)).first()


def search_categories(
    db: Session, 
    search_term: str, 
    active_only: bool = True
) -> List[Category]:
    """Search categories by name (partial match, case insensitive)"""
    query = db.query(Category).filter(
        Category.name.ilike(f"%{search_term}%")
    )
    
    if active_only:
        query = query.filter(Category.active == True)
    
    return query.order_by(Category.name).all()