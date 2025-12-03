"""
Products API Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db_connection import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product
from app.utils.dependencies import require_admin
from app.models.user import User

# Crea router per products
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ==================== ENDPOINTS PUBBLICI ====================

@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Lista prodotti (pubblico)
    
    Ora include i dati della categoria per ogni prodotto
    """
    return crud_product.get_products(db, skip, limit)


@router.get("/search", response_model=list[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1, description="Termine di ricerca"),
    active_only: bool = Query(True, description="Cerca solo prodotti attivi"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Cerca prodotti per nome (pubblico)
    
    - q: Termine da cercare (ricerca parziale, case-insensitive)
    - active_only: Se True, cerca solo prodotti attivi
    - skip: Record da saltare (paginazione)
    - limit: Numero massimo risultati
    
    Include i dati della categoria! 
    
    Esempi:
    - `/api/products/search?q=shirt` → Trova "Red T-Shirt", "Blue Shirt"
    - `/api/products/search?q=nike&active_only=false` → Trova tutti i prodotti Nike
    """
    return crud_product.search_products_by_name(db, q, active_only, skip, limit)


@router.get("/category/{category_id}", response_model=list[ProductResponse])
def get_products_by_category(
    category_id: int,
    active_only: bool = Query(True, description="Mostra solo prodotti attivi"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Filtra prodotti per categoria (pubblico)
    
    - category_id: ID della categoria
    - active_only: Se True, mostra solo prodotti attivi
    - skip: Record da saltare (paginazione)
    - limit: Numero massimo risultati
    
    Esempi:
    - `/api/products/category/1` → Tutti i prodotti della categoria 1
    - `/api/products/category/2?active_only=false` → Tutti i prodotti (anche disattivati) della categoria 2
    """
    products = crud_product.get_products_by_category(db, category_id, active_only, skip, limit)
    if not products:
        raise HTTPException(404, "Nessun prodotto trovato per questa categoria")
    return products


@router.get("/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """
    Ottieni prodotto per SKU (pubblico)
    
    Include i dati della categoria!
    """
    product = crud_product.get_product_by_sku(db, sku)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Dettaglio prodotto (pubblico)
    
    Ora include i dati completi della categoria
    """
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


# ==================== ENDPOINTS ADMIN ====================

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """
    Crea prodotto (SOLO ADMIN)
    
    Ora puoi specificare category_id
    """
    return crud_product.create_product(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    product_update: ProductUpdate,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """
    Aggiorna prodotto (SOLO ADMIN)
    
    Ora puoi cambiare anche category_id
    """
    product = crud_product.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(404, "Prodotto non trovato")
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """Elimina prodotto (SOLO ADMIN)"""
    if not crud_product.delete_product(db, product_id):
        raise HTTPException(404, "Prodotto non trovato")