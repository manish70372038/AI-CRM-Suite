"""
Unit tests for individual LangGraph tools, exercised directly (not
through the /chat endpoint) with the DB and LLM calls stubbed out.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.rep import Rep
from app.models.interaction import Interaction, InteractionType, SourceType
from app.agent.tools import (
    log_interaction,
    search_interaction,
    summarize_previous,
    recommend_followup,
    edit_interaction,
)

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add(Rep(id=1, name="Test Rep"))
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_log_interaction_tool(db_session, monkeypatch):
    monkeypatch.setattr(
        log_interaction,
        "generate_json",
        lambda messages: {
            "doctor_name": "Dr. Neha Verma",
            "hospital": "Fortis",
            "interaction_type": "call",
            "products_discussed": ["Glucobal"],
            "follow_up_date": "",
            "sentiment": "neutral",
            "summary": "Brief call about Glucobal dosing.",
        },
    )

    state = {"db": db_session, "message": "Called Dr. Neha Verma about Glucobal", "rep_id": 1}
    result = log_interaction.run(state)

    assert result["tool_name"] == "log_interaction"
    assert result["tool_result"]["doctor_name"] == "Dr. Neha Verma"


def test_search_interaction_tool(db_session, monkeypatch):
    db_session.add(
        Interaction(
            rep_id=1,
            doctor_name="Dr. Neha Verma",
            hospital="Fortis",
            interaction_type=InteractionType.call,
            products_discussed=["Glucobal"],
            source=SourceType.form,
        )
    )
    db_session.commit()

    monkeypatch.setattr(search_interaction, "generate_json", lambda messages: {"hcp_name": "Neha"})

    state = {"db": db_session, "message": "Show my meetings with Dr. Neha", "rep_id": 1}
    result = search_interaction.run(state)

    assert result["tool_result"]["count"] == 1


def test_summarize_previous_tool(db_session, monkeypatch):
    db_session.add(
        Interaction(
            rep_id=1,
            doctor_name="Dr. Neha Verma",
            interaction_type=InteractionType.call,
            products_discussed=["Glucobal"],
            summary="Positive initial reception to Glucobal.",
            source=SourceType.form,
        )
    )
    db_session.commit()

    monkeypatch.setattr(summarize_previous, "generate_json", lambda messages: {"hcp_name": "Neha Verma"})
    monkeypatch.setattr(
        summarize_previous,
        "generate",
        lambda messages: "Dr. Verma has responded well to Glucobal so far.",
    )

    state = {"db": db_session, "message": "What's the history with Dr. Neha Verma?", "rep_id": 1}
    result = summarize_previous.run(state)

    assert "Glucobal" in result["tool_result"]["briefing"]


def test_recommend_followup_tool(db_session, monkeypatch):
    db_session.add(
        Interaction(
            rep_id=1,
            doctor_name="Dr. Neha Verma",
            interaction_type=InteractionType.call,
            products_discussed=["Glucobal"],
            summary="Doctor asked for more clinical data.",
            source=SourceType.form,
        )
    )
    db_session.commit()

    monkeypatch.setattr(recommend_followup, "generate_json", lambda messages: {"hcp_name": "Neha Verma"})
    monkeypatch.setattr(
        recommend_followup,
        "generate",
        lambda messages: "Send the Phase III clinical data packet for Glucobal.",
    )

    state = {"db": db_session, "message": "What should I do next with Dr. Neha Verma?", "rep_id": 1}
    result = recommend_followup.run(state)

    assert "clinical data" in result["tool_result"]["recommendation"]


def test_edit_interaction_tool(db_session, monkeypatch):
    interaction = Interaction(
        rep_id=1,
        doctor_name="Dr. Neha Verma",
        interaction_type=InteractionType.call,
        products_discussed=["Glucobal"],
        source=SourceType.form,
    )
    db_session.add(interaction)
    db_session.commit()

    # Two sequential generate_json calls happen inside edit_interaction.run:
    # 1) search_parse_prompt to locate the target interaction
    # 2) edit_extraction_prompt to compute the diff
    call_count = {"n": 0}

    def sequenced_generate_json(messages):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return {"hcp_name": "Neha Verma"}
        return {"follow_up_action": "Send updated brochure"}

    monkeypatch.setattr(edit_interaction, "generate_json", sequenced_generate_json)

    state = {"db": db_session, "message": "Set follow up to send updated brochure", "rep_id": 1}
    result = edit_interaction.run(state)

    assert result["tool_result"]["follow_up_action"] == "Send updated brochure"