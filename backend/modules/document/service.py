from typing import Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from .repository import DocumentRepository
from ...models.document import Document


class DocumentService:
    def __init__(self, tokens: dict, client_id: str, client_secret: str, scopes: list[str]) -> None:
        self.credentials = Credentials(
            token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_uri=tokens.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )

    def refresh_if_needed(self) -> dict | None:
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            return {
                "access_token": self.credentials.token,
                "refresh_token": self.credentials.refresh_token,
                "token_uri": self.credentials.token_uri,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scopes": list(self.credentials.scopes or []),
            }
        return None

    def create_brd_doc(self, brd_json: dict) -> dict[str, Any]:
        service = build("docs", "v1", credentials=self.credentials)
        title = brd_json.get("title") or "Business Requirements Document"
        doc = service.documents().create(body={"title": title}).execute()
        doc_id = doc.get("documentId")

        requests = self._render_brd_requests(brd_json)
        if requests:
            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

        return {"document_id": doc_id}

    def _render_brd_requests(self, brd_json: dict) -> list[dict]:
        blocks = []

        doc_info = brd_json.get("document_info", {})
        if doc_info:
            blocks.append(("Document Info", _format_kv_block(doc_info)))

        exec_summary = brd_json.get("executive_summary", {})
        if exec_summary:
            blocks.append(("Executive Summary", exec_summary.get("overview", "")))
            phases = exec_summary.get("phases") or []
            if phases:
                phase_lines = []
                for phase in phases:
                    phase_lines.append(f'{phase.get("name","")}: {phase.get("summary","")}'.strip())
                    for feat in phase.get("key_features") or []:
                        phase_lines.append(f"  - {feat}")
                blocks.append(("Phases", "\n".join(phase_lines)))

        blocks.append(("Business Objectives", brd_json.get("business_objectives", [])))

        scope = brd_json.get("scope", {})
        if scope:
            in_scope = []
            for item in scope.get("in_scope") or []:
                header = item.get("name", "")
                if item.get("phase"):
                    header = f"{header} ({item.get('phase')})"
                in_scope.append(header)
                for detail in item.get("details") or []:
                    in_scope.append(f"  - {detail}")
            blocks.append(("In Scope", "\n".join(in_scope)))
            blocks.append(("Out of Scope", scope.get("out_of_scope", [])))

        blocks.append(("Platforms", _format_platforms(brd_json.get("platforms", []))))
        blocks.append(("Personas", _format_personas(brd_json.get("personas", []))))

        blocks.append(
            ("Functional Requirements", _format_feature_groups(brd_json.get("functional_requirements", [])))
        )
        blocks.append(
            ("Non-Functional Requirements", _format_category_groups(brd_json.get("non_functional_requirements", [])))
        )
        blocks.append(
            ("Technical Requirements", _format_category_groups(brd_json.get("technical_requirements", [])))
        )

        blocks.append(("Integrations", _format_integrations(brd_json.get("integrations", []))))
        blocks.append(("Data Requirements", brd_json.get("data_requirements", [])))
        blocks.append(("UI/UX Requirements", brd_json.get("ui_ux_requirements", [])))
        blocks.append(("Reporting & Analytics", brd_json.get("reporting_analytics", [])))
        blocks.append(("Support Requirements", brd_json.get("support_requirements", [])))
        blocks.append(("Assumptions", brd_json.get("assumptions", [])))
        blocks.append(("Dependencies", brd_json.get("dependencies", [])))
        blocks.append(("Risks", brd_json.get("risks", [])))
        blocks.append(("Constraints", brd_json.get("constraints", [])))
        blocks.append(("Change Control", brd_json.get("change_control", [])))
        blocks.append(("Compliance & Security", brd_json.get("compliance_security", [])))

        text_blocks = []
        for heading, content in blocks:
            if content is None or content == "" or content == []:
                continue
            text_blocks.append(f"{heading}\n")
            if isinstance(content, list):
                for item in content:
                    text_blocks.append(f"- {item}\n")
            else:
                for line in str(content).splitlines():
                    text_blocks.append(f"{line}\n")
            text_blocks.append("\n")

        full_text = "".join(text_blocks)
        if not full_text.strip():
            return []
        return [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": full_text,
                }
            }
        ]


class DocumentStore:
    def __init__(self) -> None:
        self.repo = DocumentRepository()

    def list_by_user(self, db, user_id: str, limit: int = 50):
        return self.repo.list_by_user(db, user_id, limit=limit)

    def get_by_id(self, db, document_id: str):
        return self.repo.get_by_id(db, document_id)

    def get_by_transcript_request_id(self, db, transcript_request_id: str):
        return self.repo.get_by_transcript_request_id(db, transcript_request_id)

    def create_document_record(
        self,
        db,
        user_id: str,
        transcript_request_id: str,
        google_doc_id: str,
        doc_type: str = "BRD",
    ) -> Document:
        document = Document(
            user_id=user_id,
            transcript_request_id=transcript_request_id,
            google_doc_id=google_doc_id,
            doc_type=doc_type,
        )
        return self.repo.create(db, document)

    def create_brd_sections(self, db, document_id: str, brd_json: dict):
        sections = [
            ("document_info", _format_kv_block(brd_json.get("document_info", {}))),
            ("executive_summary", (brd_json.get("executive_summary") or {}).get("overview", "")),
            ("business_objectives", "\n".join(brd_json.get("business_objectives", []))),
            ("scope", _format_scope(brd_json.get("scope", {}))),
            ("platforms", _format_platforms(brd_json.get("platforms", []))),
            ("personas", _format_personas(brd_json.get("personas", []))),
            ("functional_requirements", _format_feature_groups(brd_json.get("functional_requirements", []))),
            ("non_functional_requirements", _format_category_groups(brd_json.get("non_functional_requirements", []))),
            ("technical_requirements", _format_category_groups(brd_json.get("technical_requirements", []))),
            ("integrations", _format_integrations(brd_json.get("integrations", []))),
            ("data_requirements", "\n".join(brd_json.get("data_requirements", []))),
            ("ui_ux_requirements", "\n".join(brd_json.get("ui_ux_requirements", []))),
            ("reporting_analytics", "\n".join(brd_json.get("reporting_analytics", []))),
            ("support_requirements", "\n".join(brd_json.get("support_requirements", []))),
            ("assumptions", "\n".join(brd_json.get("assumptions", []))),
            ("dependencies", "\n".join(brd_json.get("dependencies", []))),
            ("risks", "\n".join(brd_json.get("risks", []))),
            ("constraints", "\n".join(brd_json.get("constraints", []))),
            ("change_control", "\n".join(brd_json.get("change_control", []))),
            ("compliance_security", "\n".join(brd_json.get("compliance_security", []))),
        ]
        created = []
        for key, content in sections:
            if not content:
                continue
            created.append(self.repo.create_section(db, document_id, key, None, content))
        return created


def _format_kv_block(values: dict) -> str:
    if not values:
        return ""
    lines = []
    for key, value in values.items():
        if value:
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


def _format_scope(scope: dict) -> str:
    if not scope:
        return ""
    lines = []
    for item in scope.get("in_scope") or []:
        header = item.get("name", "")
        if item.get("phase"):
            header = f"{header} ({item.get('phase')})"
        lines.append(header)
        for detail in item.get("details") or []:
            lines.append(f"  - {detail}")
    if scope.get("out_of_scope"):
        lines.append("Out of Scope:")
        for item in scope.get("out_of_scope") or []:
            lines.append(f"  - {item}")
    return "\n".join(lines)


def _format_platforms(platforms: list) -> str:
    if not platforms:
        return ""
    lines = []
    for platform in platforms:
        name = platform.get("name", "")
        type_value = platform.get("type")
        notes = platform.get("notes")
        phase = platform.get("phase")
        line = name
        if type_value:
            line = f"{line} [{type_value}]"
        if phase:
            line = f"{line} ({phase})"
        if notes:
            line = f"{line} - {notes}"
        lines.append(line)
    return "\n".join(lines)


def _format_personas(personas: list) -> str:
    if not personas:
        return ""
    lines = []
    for persona in personas:
        name = persona.get("name", "")
        description = persona.get("description")
        line = name
        if description:
            line = f"{line}: {description}"
        lines.append(line)
    return "\n".join(lines)


def _format_feature_groups(groups: list) -> str:
    if not groups:
        return ""
    lines = []
    for group in groups:
        header = group.get("name", "")
        if group.get("phase"):
            header = f"{header} ({group.get('phase')})"
        lines.append(header)
        for feature in group.get("features") or []:
            lines.append(f"  - {feature}")
    return "\n".join(lines)


def _format_category_groups(groups: list) -> str:
    if not groups:
        return ""
    lines = []
    for group in groups:
        lines.append(group.get("category", ""))
        for item in group.get("requirements") or []:
            lines.append(f"  - {item}")
    return "\n".join(lines)


def _format_integrations(items: list) -> str:
    if not items:
        return ""
    lines = []
    for item in items:
        name = item.get("name", "")
        purpose = item.get("purpose")
        notes = item.get("notes")
        line = name
        if purpose:
            line = f"{line} - {purpose}"
        if notes:
            line = f"{line} ({notes})"
        lines.append(line)
    return "\n".join(lines)
