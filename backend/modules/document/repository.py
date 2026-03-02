from sqlalchemy.orm import Session
from ...models.document import Document
from ...models.document_section import DocumentSection


class DocumentRepository:
    def create(self, db: Session, document: Document) -> Document:
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_by_id(self, db: Session, document_id: str) -> Document | None:
        return db.query(Document).filter(Document.id == document_id).first()

    def get_by_transcript_request_id(
        self, db: Session, transcript_request_id: str
    ) -> Document | None:
        return (
            db.query(Document)
            .filter(Document.transcript_request_id == transcript_request_id)
            .first()
        )

    def list_by_user(self, db: Session, user_id: str, limit: int = 50):
        return (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .all()
        )

    def create_section(
        self, db: Session, document_id: str, section_key: str, heading_id: str | None, content: str
    ) -> DocumentSection:
        section = DocumentSection(
            document_id=document_id,
            section_key=section_key,
            heading_id=heading_id,
            content=content,
        )
        db.add(section)
        db.commit()
        db.refresh(section)
        return section

    def list_sections(self, db: Session, document_id: str):
        return (
            db.query(DocumentSection)
            .filter(DocumentSection.document_id == document_id)
            .all()
        )
