from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.prodotto import Prodotto

# Crea applicazione FastAPI
app = FastAPI(
    title="E-commerce API",
    description="API con database PostgreSQL",
    version="1.0.0"
)

# CONFIGURAZIONE CORS
origins = [
    "http://localhost:3000",      # React
    "http://localhost:5173",      # Vite
    "http://localhost:4200",      # Angular
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Origini permesse
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],          # Tutti gli headers
)

# ENDPOINT ROOT

@app.get("/")
def root():
    """Pagina principale"""
    return {
        "message": "Benvenuto nell'API E-commerce!",
        "endpoints": {
            "prodotti": "/api/prodotti",
            "health": "/health",
            "docs": "/docs"
        }
    }

# ENDPOINT PRODOTTI 

# POST   → Creare un nuovo prodotto
# PUT    → Modificare un prodotto esistente
# DELETE → Eliminare un prodotto
# GET    → Ottenere informazioni su prodotto/i (singolo o lista)

@app.get("/api/prodotti")
def get_prodotti(db: Session = Depends(get_db)):
    """
    Ottieni tutti i prodotti dal database.
    Usa il Model Prodotto per fare query su PostgreSQL.
    """
    # Query con SQLAlchemy ORM
    prodotti = db.query(Prodotto).all()
    return prodotti

@app.get("/api/prodotti/{prodotto_id}")
def get_prodotto(prodotto_id: int, db: Session = Depends(get_db)):
    """
    Ottieni un singolo prodotto per ID.
    """
    prodotto = db.query(Prodotto).filter(Prodotto.id == prodotto_id).first()
    
    if not prodotto:
        return {"error": f"Prodotto {prodotto_id} non trovato"}
    
    return prodotto

# HEALTH CHECK

@app.get("/health")
def health():
    """Verifica che API sia attiva"""
    return {"status": "ok"}