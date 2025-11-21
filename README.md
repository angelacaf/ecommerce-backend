# Backend Setup

1. Crea virtual environment: `python -m venv venv`
2. Attiva: `.\venv\Scripts\activate` 
3. Installa dipendenze: `pip install -r requirements.txt`
4. Importa database:
   - Apri pgAdmin → Crea database "ecommerce"
   - Click destro sul database → Restore
   - Format: Plain, Filename: `ecommerce-backend/ecommerce_en_db.sql`


# avvio be
uvicorn app.main:app --reload

# avvio fe
npm run dev


TODO: registrazione -> login -> ordine


CRUD ordine

CREATE:
add() → flush() → [usa ID] → add(dettagli) → commit() → refresh()

READ:
query() → filter() → [first() o all()]

UPDATE:
query() → modifica attributi → commit() → refresh()

DELETE:
query() → delete() → commit()

