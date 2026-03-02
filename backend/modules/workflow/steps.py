from dataclasses import dataclass
from typing import Callable, Any
from sqlalchemy.orm import Session
from ...core.config import get_settings
from ...models.workflow import WorkflowExecution
from ..user.service import UserService
from ..transcript_request.service import TranscriptRequestService
from ..integration.fireflies import FirefliesClient, FirefliesError
from ..ai_brd.service import BRDService
from ..document.service import DocumentService, DocumentStore


@dataclass(frozen=True)
class StepDefinition:
    key: str
    handler: Callable[[Session, WorkflowExecution, dict[str, Any]], dict[str, Any] | None]
    retryable: bool


def validate_request(db: Session, execution: WorkflowExecution, context: dict[str, Any]):
    request_service = TranscriptRequestService()
    request = request_service.get(db, str(execution.transcript_request_id))
    if not request:
        raise ValueError("Transcript request not found")

    context["transcript_request_id"] = str(request.id)
    context["user_id"] = str(request.user_id)
    return {"request_status": request.status}


def ensure_transcript(db: Session, execution: WorkflowExecution, context: dict[str, Any]):
    user_service = UserService()
    request_service = TranscriptRequestService()

    request_id = context.get("transcript_request_id") or str(execution.transcript_request_id)
    request = request_service.get(db, request_id)
    if not request:
        raise ValueError("Transcript request not found")

    transcript = request_service.get_transcript(db, request_id)
    if transcript:
        return {"transcript_id": str(transcript.id)}

    fireflies_key = user_service.get_fireflies_key(db, str(request.user_id))
    if not fireflies_key:
        request_service.update_status(db, request_id, "FAILED")
        raise ValueError("Connect Fireflies to generate BRD")

    transcript_id = FirefliesClient.parse_transcript_id(request.source_link)
    if not transcript_id:
        request_service.update_status(db, request_id, "FAILED")
        raise ValueError("Invalid Fireflies transcript link")

    client = FirefliesClient(fireflies_key)
    transcript_data = client.poll_transcript(transcript_id)
    raw_text = _render_fireflies_transcript(transcript_data)
    cleaned_text = _clean_transcript(raw_text)

    stored = request_service.upsert_transcript(
        db, request_id, "fireflies", raw_text, cleaned_text
    )
    request_service.update_status(db, request_id, "COMPLETED")
    return {"transcript_id": str(stored.id)}


def generate_brd(db: Session, execution: WorkflowExecution, context: dict[str, Any]):
    settings = get_settings()
    request_service = TranscriptRequestService()

    request_id = context.get("transcript_request_id") or str(execution.transcript_request_id)
    transcript = request_service.get_transcript(db, request_id)
    if not transcript:
        raise ValueError("Transcript missing")

    brd_service = BRDService(api_key=settings.openai_api_key, model=settings.openai_model)
    brd_json = brd_service.generate_brd(transcript.cleaned_text or transcript.raw_text)
    context["brd_json"] = brd_json
    return {"brd_generated": True}


def create_document(db: Session, execution: WorkflowExecution, context: dict[str, Any]):
    settings = get_settings()
    user_service = UserService()
    request_service = TranscriptRequestService()
    document_store = DocumentStore()

    request_id = context.get("transcript_request_id") or str(execution.transcript_request_id)
    request = request_service.get(db, request_id)
    if not request:
        raise ValueError("Transcript request not found")

    existing = document_store.repo.get_by_transcript_request_id(db, request_id)
    if existing:
        context["google_doc_id"] = existing.google_doc_id
        context["document_id"] = str(existing.id)
        return {"google_doc_id": existing.google_doc_id}

    tokens = user_service.get_google_tokens(db, str(request.user_id))
    if not tokens:
        raise ValueError("Missing Google OAuth tokens")

    doc_service = DocumentService(
        tokens=tokens,
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        scopes=settings.google_docs_scopes,
    )
    refreshed = doc_service.refresh_if_needed()
    if refreshed:
        user_service.upsert_google_tokens(db, str(request.user_id), refreshed)

    brd_json = context.get("brd_json")
    if not brd_json:
        raise ValueError("BRD JSON missing from context")

    result = doc_service.create_brd_doc(brd_json)
    context["google_doc_id"] = result["document_id"]
    return {"google_doc_id": result["document_id"]}


def link_document(db: Session, execution: WorkflowExecution, context: dict[str, Any]):
    request_service = TranscriptRequestService()
    document_store = DocumentStore()

    request_id = context.get("transcript_request_id") or str(execution.transcript_request_id)
    request = request_service.get(db, request_id)
    if not request:
        raise ValueError("Transcript request not found")

    google_doc_id = context.get("google_doc_id")
    if not google_doc_id:
        raise ValueError("Google Doc ID missing")

    existing = document_store.repo.get_by_transcript_request_id(db, request_id)
    if not existing:
        document = document_store.create_document_record(
            db, str(request.user_id), request_id, google_doc_id
        )
        context["document_id"] = str(document.id)
        brd_json = context.get("brd_json") or {}
        document_store.create_brd_sections(db, str(document.id), brd_json)
    request_service.update_status(db, request_id, "PROCESSED")
    return {"linked": True}


def _render_fireflies_transcript(transcript_data: dict) -> str:
    sentences = transcript_data.get("sentences") or []
    lines = []
    for sentence in sentences:
        speaker = sentence.get("speaker_name") or "Speaker"
        text = sentence.get("text") or ""
        if text:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines).strip()


def _clean_transcript(text: str) -> str:
    if not text:
        return ""
    parts = text.replace("\r", "\n").splitlines()
    compact = " ".join(line.strip() for line in parts if line.strip())
    return compact.strip()


WORKFLOW_STEPS = [
    StepDefinition(key="VALIDATE_REQUEST", handler=validate_request, retryable=False),
    StepDefinition(key="ENSURE_TRANSCRIPT", handler=ensure_transcript, retryable=True),
    StepDefinition(key="GENERATE_BRD", handler=generate_brd, retryable=True),
    StepDefinition(key="CREATE_DOCUMENT", handler=create_document, retryable=True),
    StepDefinition(key="LINK_DOCUMENT", handler=link_document, retryable=True),
]
