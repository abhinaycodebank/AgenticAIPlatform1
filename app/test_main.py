import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db

# 1. Setup isolated in-memory testing database configurations
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Establish a override dependency function injection
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the app database session bindings
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Builds completely clean tables before running every single isolated unit test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# =====================================================================
# INTEGRATION TESTING MATRIX SUITE
# =====================================================================

def test_root_endpoint():
    """Verifies backend entry point server is live."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Platform backend is live!"}

def test_create_agent_profile():
    """Verifies that an agent saves and serializes its configurations safely."""
    payload = {
        "name": "Audit Test Agent",
        "system_prompt": "Analyze numbers strictly.",
        "llm_model": "gpt-4o-mini",
        "llm_provider": "openai",
        "personality": "Meticulous",
        "memory_enabled": True,
        "execution_limits": {"max_tokens": 1500}
    }
    response = client.post("/agents/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Audit Test Agent"
    assert data["memory_enabled"] is True
    assert data["execution_limits"] == {"max_tokens": 1500}

def test_prevent_duplicate_agent_names():
    """Verifies that unique index naming integrity guards against dirty writes."""
    payload = {
        "name": "Clone Bot",
        "system_prompt": "Instructions text",
        "personality": "None"
    }
    # First write succeeds
    res1 = client.post("/agents/", json=payload)
    assert res1.status_code == 200
    
    # Second microsecond write must be gracefully blocked
    res2 = client.post("/agents/", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Agent name already exists"
