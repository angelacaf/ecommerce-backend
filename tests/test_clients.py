"""
Test automatici per endpoints Clients
"""
import sys
import os

# Aggiungi la cartella parent (root del progetto) al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ==================== SETUP DATABASE TEST ====================

# Database in memoria per i test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override della funzione get_db per usare il database di test"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db

# Crea le tabelle
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)


# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def test_client():
    """Crea un nuovo client per ogni test"""
    import uuid
    unique_email = f"test-{uuid.uuid4()}@example.com"
    data = {
        "email": unique_email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+39 333 1234567",
        "country": "Italy"
    }
    response = client.post("/api/clients/register", json=data)
    assert response.status_code == 201, f"Failed to create test client: {response.json()}"
    return response.json()


# ==================== TEST REGISTRAZIONE ====================

def test_register_client():
    """Test registrazione nuovo cliente"""
    import uuid
    unique_email = f"newuser-{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/clients/register",
        json={
            "email": unique_email,
            "password": "securepass123",
            "first_name": "Mario",
            "last_name": "Rossi",
            "country": "Italy"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == unique_email
    assert data["first_name"] == "Mario"
    assert "password" not in data  # Password non deve essere nella risposta
    assert "password_hash" not in data  # Hash non deve essere nella risposta
    assert data["active"] == True
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email():
    """Test registrazione con email duplicata (deve fallire)"""
    import uuid
    unique_email = f"duplicate-{uuid.uuid4()}@example.com"
    client_data = {
        "email": unique_email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Prima registrazione - OK
    response1 = client.post("/api/clients/register", json=client_data)
    assert response1.status_code == 201
    
    # Seconda registrazione - FAIL
    response2 = client.post("/api/clients/register", json=client_data)
    assert response2.status_code == 400
    assert "già registrata" in response2.json()["detail"].lower()


def test_register_invalid_email():
    """Test registrazione con email non valida"""
    response = client.post(
        "/api/clients/register",
        json={
            "email": "invalid-email",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 422  # Validation error


def test_register_short_password():
    """Test registrazione con password troppo corta"""
    response = client.post(
        "/api/clients/register",
        json={
            "email": "test@example.com",
            "password": "123",  # Troppo corta (min 6)
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 422


# ==================== TEST LOGIN ====================

def test_login_success(test_client):
    """Test login con credenziali corrette"""
    response = client.post(
        "/api/clients/login",
        json={
            "email": test_client["email"],  # Usa l'email dalla fixture
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_client["email"]
    assert "password" not in data


def test_login_wrong_password(test_client):
    """Test login con password sbagliata"""
    response = client.post(
        "/api/clients/login",
        json={
            "email": test_client["email"],  # Usa l'email dalla fixture
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "non corretti" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test login con utente inesistente"""
    response = client.post(
        "/api/clients/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401


# ==================== TEST GET CLIENTS ====================

def test_get_clients_list(test_client):
    """Test lista clienti"""
    response = client.get("/api/clients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_client_by_id(test_client):
    """Test dettaglio cliente per ID"""
    client_id = test_client["id"]
    response = client.get(f"/api/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["email"] == test_client["email"]  # Usa l'email dalla fixture


def test_get_nonexistent_client():
    """Test get cliente inesistente"""
    response = client.get("/api/clients/99999")
    assert response.status_code == 404


def test_get_client_by_email(test_client):
    """Test cerca cliente per email"""
    response = client.get(f"/api/clients/email/{test_client['email']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_client["email"]


# ==================== TEST UPDATE CLIENT ====================

def test_update_client(test_client):
    """Test aggiornamento cliente"""
    client_id = test_client["id"]
    response = client.put(
        f"/api/clients/{client_id}",
        json={
            "first_name": "UpdatedName",
            "phone": "+39 333 9999999"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedName"
    assert data["phone"] == "+39 333 9999999"
    assert data["last_name"] == "User"  # Non modificato


def test_update_nonexistent_client():
    """Test update cliente inesistente"""
    response = client.put(
        "/api/clients/99999",
        json={"first_name": "Test"}
    )
    assert response.status_code == 404


# ==================== TEST CHANGE PASSWORD ====================

def test_change_password(test_client):
    """Test cambio password"""
    client_id = test_client["id"]
    response = client.post(
        f"/api/clients/{client_id}/change-password",
        json={
            "old_password": "password123",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == 200
    
    # Verifica che il login funzioni con la nuova password
    login_response = client.post(
        "/api/clients/login",
        json={
            "email": test_client["email"],  # Usa l'email dalla fixture
            "password": "newpassword456"
        }
    )
    assert login_response.status_code == 200


def test_change_password_wrong_old_password(test_client):
    """Test cambio password con vecchia password sbagliata"""
    client_id = test_client["id"]
    response = client.post(
        f"/api/clients/{client_id}/change-password",
        json={
            "old_password": "wrongpassword",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == 400


# ==================== TEST DELETE CLIENT ====================

def test_delete_client(test_client):
    """Test eliminazione cliente (soft delete)"""
    client_id = test_client["id"]
    
    # Elimina
    response = client.delete(f"/api/clients/{client_id}")
    assert response.status_code == 204
    
    # Verifica che il cliente non sia più visibile nella lista (active=False)
    list_response = client.get("/api/clients?active_only=true")
    client_ids = [c["id"] for c in list_response.json()]
    assert client_id not in client_ids


def test_delete_nonexistent_client():
    """Test delete cliente inesistente"""
    response = client.delete("/api/clients/99999")
    assert response.status_code == 404


# ==================== CLEANUP ====================
# Il database test.db verrà sovrascritto al prossimo test
# Su Windows, eliminarlo automaticamente può causare PermissionError