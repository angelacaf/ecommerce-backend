# Backend Setup

1. Crea virtual environment: `python -m venv venv`
2. Attiva: `.\venv\Scripts\activate` 
3. Installa dipendenze: `pip install -r requirements.txt`
4. Importa database:
   - Apri pgAdmin → Crea database "ecommerce"
   - Click destro sul database → Restore
   - Format: Plain, Filename: `ecommerce-backend/ecommerce_en_db.sql`
5. Configurazione ambiente
   - .env in fe   ->   VITE_BACKEND_URL=[your_backend_url_here/api]
      ad esempio       VITE_BACKEND_URL=http://localhost:8000/api
   - .env in be   ->   DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
      ad esempio       DATABASE_URL=postgresql://postgres:root@localhost:5432/ecommerce 

# avvio be
uvicorn app.main:app --reload

# avvio fe
npm run dev





