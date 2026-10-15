"""FastAPI application for the Aegis policy assistant."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .config import settings
from .models import Question
from .pipeline import answer_question


app = FastAPI(title=settings.app_name, description="Cited answers from company policies")
WEB_PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Serve the simple web client."""
    return FileResponse(WEB_PAGE)


@app.get("/health")
def health() -> dict[str, str]:
    """Basic process health check (database readiness will be added later)."""
    return {"status": "ok"}


@app.get("/documents")
def list_documents() -> dict[str, list[dict[str, str]]]:
    """List indexed policy documents."""
    return {"documents": []}


@app.post("/ask")
def ask(payload: Question) -> dict[str, object]:
    """Ask a policy question as a demo user."""
    result = answer_question(payload)
    return {"answer": result.text, "sources": list(result.sources), "warning": result.warning}
