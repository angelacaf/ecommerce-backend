"""
Products API Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db_connection import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product

# Crea router per products
router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """Lista prodotti"""
    return crud_product.get_products(db, skip, limit)


@router.get("/products/search", response_model=list[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1, description="Termine di ricerca"),
    active_only: bool = Query(True, description="Cerca solo prodotti attivi"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Cerca prodotti per nome
    
    - q: Termine da cercare (ricerca parziale, case-insensitive)
    - active_only: Se True, cerca solo prodotti attivi
    - skip: Record da saltare (paginazione)
    - limit: Numero massimo risultati
    
    Esempi:
    - `/products/search?q=shirt` → Trova "Red T-Shirt", "Blue Shirt"
    - `/products/search?q=nike&active_only=false` → Trova tutti i prodotti Nike
    """
    return crud_product.search_products_by_name(db, q, active_only, skip, limit)


@router.get("/products/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Ottieni prodotto per SKU"""
    product = crud_product.get_product_by_sku(db, sku)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Dettaglio prodotto"""
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Crea prodotto"""
    return crud_product.create_product(db, product)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Aggiorna prodotto"""
    product = crud_product.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Elimina prodotto"""
    if not crud_product.delete_product(db, product_id):
        raise HTTPException(404, "Prodotto non trovato")