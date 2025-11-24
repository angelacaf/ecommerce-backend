from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db_connection import get_db
from app.schemas.category import CategoryResponse
from app.crud import category as crud_category

router = APIRouter(prefix="/categories", 
                  # tags=["categories"]
                   )

@router.get("/", response_model=list[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    return crud_category.get_categories(db)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud_category.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category