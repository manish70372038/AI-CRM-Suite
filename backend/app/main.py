"""
FastAPI application entrypoint.

Responsibilities:
- Instantiate the FastAPI app and configure CORS for the React frontend.
- Register all routers (hcp, interaction, chat).
- On startup, create tables if they don't exist and seed a single
  default Rep row (id=1) — matching the single-tenant scope agreed
  in the architecture (no auth/login flow for this assignment), and
  matching the hardcoded rep_id the frontend sends.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models.rep import Rep
from app.routers import chat_router, hcp_router, interaction_router

app = FastAPI(
    title="AI-First CRM — HCP Module API",
    description="Backend for the Log Interaction screen: structured form + LangGraph-powered chat.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hcp_router)
app.include_router(interaction_router)
app.include_router(chat_router)


@app.on_event("startup")
def on_startup():
    """
    Dev-mode bootstrap: creates all tables if they don't exist yet and
    seeds a default Rep so the frontend's hardcoded rep_id=1 always
    resolves. In a production deployment this would be replaced by
    Alembic migrations run as a separate step.
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        default_rep = db.query(Rep).filter(Rep.id == 1).first()
        if not default_rep:
            db.add(Rep(id=1, name="Field Rep", email="rep@example.com", region="North Region"))
            db.commit()
    finally:
        db.close()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ai-crm-hcp-backend"}