"""
Test suite per gli endpoint Products API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import Base, get_db
from app.models.product import Product


# ==================== SETUP DATABASE TEST ====================

# Database SQLite in memoria per i test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override del database dependency per usare il DB di test"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Crea e pulisce il database per ogni test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Client di test FastAPI"""
    return TestClient(app)


@pytest.fixture
def sample_product_data():
    """Dati di esempio per un prodotto"""
    return {
        "name": "iPhone 15 Pro",
        "description": "Ultimo modello di iPhone con chip A17",
        "price": 1299.99,
        "available_quantity": 50,
        "image_url": "https://example.com/iphone15.jpg",
        "sku": "IPH15PRO-256-BLK",
        "active": True,
        "featured": True
    }


@pytest.fixture
def create_test_product(client, sample_product_data):
    """Helper per creare un prodotto di test"""
    def _create_product(data=None):
        product_data = data or sample_product_data
        response = client.post("/api/products", json=product_data)
        return response.json()
    return _create_product


# ==================== TEST GET /products (LIST) ====================

def test_list_products_empty(client):
    """Test lista prodotti quando il database è vuoto"""
    response = client.get("/api/products")
    
    assert response.status_code == 200
    assert response.json() == []


def test_list_products_with_data(client, create_test_product):
    """Test lista prodotti con dati presenti"""
    # Crea 3 prodotti
    create_test_product()
    create_test_product({"name": "iPad Air", "price": 699.99, "available_quantity": 30})
    create_test_product({"name": "MacBook Pro", "price": 2499.99, "available_quantity": 20})
    
    response = client.get("/api/products")
    
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    assert products[0]["name"] == "iPhone 15 Pro"
    assert products[1]["name"] == "iPad Air"


def test_list_products_pagination(client, create_test_product):
    """Test paginazione lista prodotti"""
    # Crea 5 prodotti
    for i in range(5):
        create_test_product({"name": f"Prodotto {i}", "price": 100.0 * i, "available_quantity": 10})
    
    # Test skip=0, limit=2
    response = client.get("/api/products?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test skip=2, limit=2
    response = client.get("/api/products?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test skip=4, limit=2
    response = client.get("/api/products?skip=4&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_products_only_active(client, create_test_product):
    """Test che la lista mostri solo prodotti attivi"""
    # Crea prodotto attivo
    product1 = create_test_product({"name": "Attivo", "price": 100.0, "available_quantity": 10})
    
    # Crea prodotto e poi disattivalo
    product2 = create_test_product({"name": "Inattivo", "price": 200.0, "available_quantity": 5})
    client.delete(f"/api/products/{product2['id']}")
    
    response = client.get("/api/products")
    
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Attivo"


# ==================== TEST GET /products/{id} (DETAIL) ====================

def test_get_product_by_id(client, create_test_product):
    """Test recupero prodotto per ID"""
    created = create_test_product()
    product_id = created["id"]
    
    response = client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == product_id
    assert product["name"] == "iPhone 15 Pro"
    assert product["price"] == 1299.99
    assert "created_at" in product
    assert "updated_at" in product


def test_get_product_not_found(client):
    """Test recupero prodotto inesistente"""
    response = client.get("/api/products/99999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Prodotto non trovato"


def test_get_product_invalid_id(client):
    """Test recupero prodotto con ID non valido"""
    response = client.get("/api/products/invalid")
    
    assert response.status_code == 422  # Unprocessable Entity


# ==================== TEST POST /products (CREATE) ====================

def test_create_product_success(client, sample_product_data):
    """Test creazione prodotto con successo"""
    response = client.post("/api/products", json=sample_product_data)
    
    assert response.status_code == 201
    product = response.json()
    assert product["name"] == sample_product_data["name"]
    assert product["price"] == sample_product_data["price"]
    assert product["available_quantity"] == sample_product_data["available_quantity"]
    assert "id" in product
    assert "created_at" in product
    assert "updated_at" in product


def test_create_product_minimal_data(client):
    """Test creazione prodotto con dati minimi richiesti"""
    minimal_data = {
        "name": "Prodotto Minimo",
        "price": 9.99
    }
    
    response = client.post("/api/products", json=minimal_data)
    
    assert response.status_code == 201
    product = response.json()
    assert product["name"] == "Prodotto Minimo"
    assert product["price"] == 9.99
    assert product["available_quantity"] == 0  # Default
    assert product["active"] is True  # Default
    assert product["featured"] is False  # Default
    assert product["description"] is None
    assert product["image_url"] is None
    assert product["sku"] is None


def test_create_product_missing_required_fields(client):
    """Test creazione prodotto senza campi obbligatori"""
    # Manca il nome
    response = client.post("/api/products", json={"price": 100.0})
    assert response.status_code == 422
    
    # Manca il prezzo
    response = client.post("/api/products", json={"name": "Test"})
    assert response.status_code == 422
    
    # Entrambi mancanti
    response = client.post("/api/products", json={})
    assert response.status_code == 422


def test_create_product_invalid_price(client):
    """Test creazione prodotto con prezzo non valido"""
    invalid_data = {
        "name": "Test",
        "price": "not-a-number"
    }
    
    response = client.post("/api/products", json=invalid_data)
    assert response.status_code == 422


def test_create_product_negative_quantity(client):
    """Test creazione prodotto con quantità negativa"""
    data = {
        "name": "Test",
        "price": 100.0,
        "available_quantity": -5
    }
    
    response = client.post("/api/products", json=data)
    # Dovrebbe accettare (non c'è validazione per quantità negativa nel modello)
    # Ma è un test utile per evidenziare questo caso
    assert response.status_code == 201


# ==================== TEST PUT /products/{id} (UPDATE) ====================

def test_update_product_full(client, create_test_product):
    """Test aggiornamento completo prodotto"""
    created = create_test_product()
    product_id = created["id"]
    
    update_data = {
        "name": "iPhone 15 Pro Max",
        "description": "Versione aggiornata",
        "price": 1499.99,
        "available_quantity": 100,
        "sku": "IPH15PROMAX-512-BLK",
        "featured": False
    }
    
    response = client.put(f"/api/products/{product_id}", json=update_data)
    
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "iPhone 15 Pro Max"
    assert product["price"] == 1499.99
    assert product["available_quantity"] == 100
    assert product["featured"] is False


def test_update_product_partial(client, create_test_product):
    """Test aggiornamento parziale prodotto"""
    created = create_test_product()
    product_id = created["id"]
    
    # Aggiorna solo il prezzo
    update_data = {"price": 999.99}
    
    response = client.put(f"/api/products/{product_id}", json=update_data)
    
    assert response.status_code == 200
    product = response.json()
    assert product["price"] == 999.99
    assert product["name"] == "iPhone 15 Pro"  # Nome rimane invariato


def test_update_product_not_found(client):
    """Test aggiornamento prodotto inesistente"""
    update_data = {"price": 999.99}
    
    response = client.put("/api/products/99999", json=update_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Prodotto non trovato"


def test_update_product_empty_body(client, create_test_product):
    """Test aggiornamento con body vuoto"""
    created = create_test_product()
    product_id = created["id"]
    
    response = client.put(f"/api/products/{product_id}", json={})
    
    # Dovrebbe funzionare ma non cambiare nulla
    assert response.status_code == 200


def test_update_product_change_active_status(client, create_test_product):
    """Test cambio stato attivo/inattivo"""
    created = create_test_product()
    product_id = created["id"]
    
    # Disattiva prodotto
    response = client.put(f"/api/products/{product_id}", json={"active": False})
    
    assert response.status_code == 200
    assert response.json()["active"] is False
    
    # Riattiva prodotto
    response = client.put(f"/api/products/{product_id}", json={"active": True})
    
    assert response.status_code == 200
    assert response.json()["active"] is True


# ==================== TEST DELETE /products/{id} ====================

def test_delete_product_success(client, create_test_product):
    """Test eliminazione prodotto con successo (soft delete)"""
    created = create_test_product()
    product_id = created["id"]
    
    response = client.delete(f"/api/products/{product_id}")
    
    assert response.status_code == 204
    
    # Verifica che il prodotto non appaia più nella lista
    list_response = client.get("/api/products")
    products = list_response.json()
    assert len(products) == 0
    
    # Ma può ancora essere recuperato per ID (soft delete)
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["active"] is False


def test_delete_product_not_found(client):
    """Test eliminazione prodotto inesistente"""
    response = client.delete("/api/products/99999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Prodotto non trovato"


def test_delete_product_already_deleted(client, create_test_product):
    """Test eliminazione prodotto già eliminato"""
    created = create_test_product()
    product_id = created["id"]
    
    # Prima eliminazione
    response1 = client.delete(f"/api/products/{product_id}")
    assert response1.status_code == 204
    
    # Seconda eliminazione
    response2 = client.delete(f"/api/products/{product_id}")
    # Il prodotto esiste ma è già inattivo, quindi dovrebbe funzionare
    assert response2.status_code == 204


# ==================== TEST SCENARI COMPLESSI ====================

def test_product_lifecycle(client, sample_product_data):
    """Test ciclo di vita completo di un prodotto"""
    # 1. Crea prodotto
    create_response = client.post("/api/products", json=sample_product_data)
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # 2. Leggi prodotto
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "iPhone 15 Pro"
    
    # 3. Aggiorna prodotto
    update_response = client.put(
        f"/api/products/{product_id}",
        json={"price": 1199.99, "available_quantity": 30}
    )
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 1199.99
    
    # 4. Verifica nella lista
    list_response = client.get("/api/products")
    assert len(list_response.json()) == 1
    
    # 5. Elimina prodotto
    delete_response = client.delete(f"/api/products/{product_id}")
    assert delete_response.status_code == 204
    
    # 6. Verifica che non sia più nella lista
    final_list = client.get("/api/products")
    assert len(final_list.json()) == 0


def test_multiple_products_management(client):
    """Test gestione multipla di prodotti"""
    # Crea 10 prodotti
    product_ids = []
    for i in range(10):
        data = {
            "name": f"Prodotto {i}",
            "price": 100.0 + (i * 50),
            "available_quantity": 10 + i
        }
        response = client.post("/api/products", json=data)
        product_ids.append(response.json()["id"])
    
    # Verifica che tutti siano stati creati
    list_response = client.get("/api/products?limit=100")
    assert len(list_response.json()) == 10
    
    # Aggiorna alcuni
    for product_id in product_ids[:3]:
        client.put(f"/api/products/{product_id}", json={"featured": True})
    
    # Elimina alcuni
    for product_id in product_ids[7:]:
        client.delete(f"/api/products/{product_id}")
    
    # Verifica risultato finale
    final_list = client.get("/api/products?limit=100")
    assert len(final_list.json()) == 7  # 10 - 3 eliminati


def test_product_with_special_characters(client):
    """Test prodotto con caratteri speciali nel nome e descrizione"""
    data = {
        "name": "Prodotto 'Speciale' & Unico™",
        "description": "Descrizione con <html> & caratteri € £ ¥",
        "price": 99.99,
        "sku": "SPEC-2024-ÜÖÄ"
    }
    
    response = client.post("/api/products", json=data)
    
    assert response.status_code == 201
    product = response.json()
    assert "Speciale" in product["name"]
    assert "&" in product["description"]


# ==================== TEST EDGE CASES ====================

def test_product_with_zero_price(client):
    """Test prodotto con prezzo zero"""
    data = {
        "name": "Prodotto Gratis",
        "price": 0.0
    }
    
    response = client.post("/api/products", json=data)
    
    assert response.status_code == 201
    assert response.json()["price"] == 0.0


def test_product_with_very_long_name(client):
    """Test prodotto con nome molto lungo"""
    long_name = "A" * 300  # Oltre il limite di 200 caratteri
    data = {
        "name": long_name,
        "price": 100.0
    }
    
    response = client.post("/api/products", json=data)
    
    # Dovrebbe fallire per limite lunghezza (se implementato a livello DB)
    # O essere troncato a 200 caratteri
    # Per ora accetta qualsiasi lunghezza, ma è un caso da considerare


def test_product_with_very_high_price(client):
    """Test prodotto con prezzo molto alto"""
    data = {
        "name": "Prodotto Lusso",
        "price": 999999999.99
    }
    
    response = client.post("/api/products", json=data)
    
    assert response.status_code == 201
    assert response.json()["price"] == 999999999.99


def test_concurrent_updates(client, create_test_product):
    """Test aggiornamenti concorrenti dello stesso prodotto"""
    created = create_test_product()
    product_id = created["id"]
    
    # Simula due aggiornamenti quasi simultanei
    response1 = client.put(f"/api/products/{product_id}", json={"price": 100.0})
    response2 = client.put(f"/api/products/{product_id}", json={"price": 200.0})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # L'ultimo aggiornamento dovrebbe prevalere
    final = client.get(f"/api/products/{product_id}")
    assert final.json()["price"] == 200.0


# ==================== TEST VALIDAZIONE DATI ====================

def test_product_price_validation(client):
    """Test validazione formato prezzo"""
    # Prezzo con troppe cifre decimali
    data = {
        "name": "Test",
        "price": 99.999999
    }
    
    response = client.post("/api/products", json=data)
    assert response.status_code == 201
    # Il database potrebbe troncare o arrotondare


def test_product_url_validation(client):
    """Test con URL immagine non valido"""
    data = {
        "name": "Test",
        "price": 100.0,
        "image_url": "not-a-valid-url"
    }
    
    response = client.post("/api/products", json=data)
    # Attualmente non c'è validazione URL, quindi passa
    assert response.status_code == 201


def test_product_boolean_fields(client):
    """Test campi booleani"""
    data = {
        "name": "Test",
        "price": 100.0,
        "active": True,
        "featured": False
    }
    
    response = client.post("/api/products", json=data)
    
    assert response.status_code == 201
    product = response.json()
    assert product["active"] is True
    assert product["featured"] is False


# ==================== PERFORMANCE TESTS ====================

def test_list_products_performance(client, create_test_product):
    """Test performance con molti prodotti"""
    # Crea 100 prodotti
    for i in range(100):
        create_test_product({
            "name": f"Prodotto {i}",
            "price": float(i),
            "available_quantity": i
        })
    
    # Verifica che la query funzioni
    response = client.get("/api/products?limit=100")
    assert response.status_code == 200
    assert len(response.json()) == 100


# ==================== CLEANUP ====================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup dopo ogni test"""
    yield
    # Qui potresti aggiungere logica di cleanup se necessaria