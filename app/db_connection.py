"""
Database connection setup
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Crea engine per connettersi a PostgreSQL
engine = create_engine(DATABASE_URL)

# Crea SessionLocal per fare query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per creare i models
Base = declarative_base()


def get_db():
    """Funzione per ottenere sessione database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()