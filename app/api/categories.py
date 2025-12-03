"""
Categories API Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.schemas.category import CategoryResponse
from app.schemas.product import ProductResponse
from app.crud import category as crud_category
from app.crud import product as crud_product

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ==================== ENDPOINTS CATEGORIE ====================

@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    active_only: bool = Query(True, description="Mostra solo categorie attive"),
    db: Session = Depends(get_db)
):
    """
    Lista tutte le categorie
    
    - active_only: Se True, mostra solo categorie attive (default: True)
    """
    return crud_category.get_categories(db, active_only)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int, 
    db: Session = Depends(get_db)
):
    """
    Dettaglio singola categoria
    """
    category = crud_category.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria non trovata")
    return category


# ==================== PRODOTTI DI UNA CATEGORIA ====================

@router.get("/{category_id}/products", response_model=list[ProductResponse])
async def get_category_products(
    category_id: int,
    active_only: bool = Query(True, description="Mostra solo prodotti attivi"),
    skip: int = Query(0, ge=0, description="Numero di prodotti da saltare (paginazione)"),
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di prodotti da restituire"),
    db: Session = Depends(get_db)
):
    """
    Ottieni tutti i prodotti di una categoria specifica 

    """
    # Verifica che la categoria esista
    category = crud_category.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=404, 
            detail=f"Categoria con ID {category_id} non trovata"
        )
    
    # Ottieni i prodotti della categoria
    products = crud_product.get_products_by_category(
        db=db,
        category_id=category_id,
        active_only=active_only,
        skip=skip,
        limit=limit
    )
    
    if not products:
        raise HTTPException(
            status_code=404,
            detail=f"Nessun prodotto trovato per la categoria '{category.name}'"
        )
    
    return products