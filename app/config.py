"""
Configurazione applicazione
"""
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente da .env
load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ecommerce_db"
)

# JWT
SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "CHANGE-ME-IN-PRODUCTION-USE-A-SECURE-KEY"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "200"))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# App
APP_NAME = "E-commerce API"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"