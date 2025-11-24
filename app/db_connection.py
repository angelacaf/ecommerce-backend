from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carica file .env
load_dotenv()

# Leggi URL database
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea engine per connettersi a PostgreSQL
engine = create_engine(DATABASE_URL)

# Crea SessionLocal per fare query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per creare i models
Base = declarative_base()

# Funzione per ottenere sessione database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()