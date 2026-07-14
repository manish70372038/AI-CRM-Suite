"""
Tests for the /interaction REST endpoints. Uses an in-memory SQLite
database so tests run without a real Postgres/MySQL instance.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.rep import Rep

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool keeps a single shared connection alive for the in-memory
# DB across the whole test session; otherwise each new Session() call
# would open a fresh, empty in-memory database.
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Rep(id=1, name="Test Rep", email="rep@test.com"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_and_get_interaction():
    payload = {
        "rep_id": 1,
        "doctor_name": "Dr. Ayesha Sharma",
        "hospital": "Apollo Hospital",
        "interaction_type": "visit",
        "products_discussed": ["Cardivex"],
        "summary": "Discussed Cardivex efficacy data.",
        "sentiment": "positive",
    }
    response = client.post("/interaction", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["doctor_name"] == "Dr. Ayesha Sharma"
    interaction_id = body["id"]

    get_response = client.get(f"/interaction/{interaction_id}")
    assert get_response.status_code == 200
    assert get_response.json()["hospital"] == "Apollo Hospital"


def test_update_interaction():
    create_response = client.post(
        "/interaction",
        json={
            "rep_id": 1,
            "doctor_name": "Dr. Rohan Mehta",
            "interaction_type": "call",
        },
    )
    interaction_id = create_response.json()["id"]

    update_response = client.put(
        f"/interaction/{interaction_id}",
        json={"follow_up_action": "Send updated clinical brochure"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["follow_up_action"] == "Send updated clinical brochure"


def test_list_interactions_filters_by_doctor():
    client.post("/interaction", json={"rep_id": 1, "doctor_name": "Dr. Kavya Nair"})
    response = client.get("/interaction", params={"hcp_name": "Kavya"})
    assert response.status_code == 200
    results = response.json()
    assert any("Kavya" in r["doctor_name"] for r in results)


def test_get_missing_interaction_returns_404():
    response = client.get("/interaction/999999")
    assert response.status_code == 404