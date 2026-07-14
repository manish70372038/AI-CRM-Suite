"""
Tests for POST /chat — the conversational Log Interaction path.

The Groq LLM calls are monkeypatched so tests run deterministically
and without needing a real GROQ_API_KEY or network access.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.rep import Rep
import app.agent.graph as graph_module
import app.agent.tools.log_interaction as log_tool_module

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


def fake_generate_json(messages, **kwargs):
    system = messages[0]["content"]
    if "Classify the user's latest message" in system:
        return {"intent": "log_interaction"}
    if "Extract and return ONLY this JSON structure" in system:
        return {
            "doctor_name": "Dr. Ayesha Sharma",
            "hospital": "Apollo Hospital",
            "interaction_type": "visit",
            "products_discussed": ["Cardivex"],
            "follow_up_date": "",
            "sentiment": "positive",
            "summary": "Met Dr. Sharma to discuss Cardivex; response was positive.",
        }
    return {}


def fake_generate(messages, **kwargs):
    return "Got it — logged your visit with Dr. Ayesha Sharma."


@pytest.fixture(autouse=True)
def setup_db_and_patches(monkeypatch):
    app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Rep(id=1, name="Test Rep", email="rep@test.com"))
    db.commit()
    db.close()

    monkeypatch.setattr(graph_module, "generate_json", fake_generate_json)
    monkeypatch.setattr(graph_module, "generate", fake_generate)
    monkeypatch.setattr(log_tool_module, "generate_json", fake_generate_json)

    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_chat_logs_interaction_via_agent():
    response = client.post(
        "/chat",
        json={"rep_id": 1, "message": "Met Dr. Sharma at Apollo, discussed Cardivex, went well"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "log_interaction"
    assert "Ayesha Sharma" in body["tool_result"]["doctor_name"]
    assert body["reply"]


def test_chat_creates_new_session_when_none_given():
    response = client.post("/chat", json={"rep_id": 1, "message": "Met Dr. Sharma at Apollo"})
    assert response.status_code == 200
    assert isinstance(response.json()["session_id"], int)