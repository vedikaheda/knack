from sqlalchemy.orm import Session
from .repository import TranscriptRequestRepository


class TranscriptRequestService:
    def __init__(self) -> None:
        self.repo = TranscriptRequestRepository()

    def create(self, db: Session, user_id: str, source_link: str):
        return self.repo.create(db, user_id, source_link)

    def get(self, db: Session, request_id: str):
        return self.repo.get(db, request_id)

    def list_by_user(self, db: Session, user_id: str, limit: int = 50):
        return self.repo.list_by_user(db, user_id, limit=limit)

    def update_status(self, db: Session, request_id: str, status: str):
        request = self.repo.get(db, request_id)
        if not request:
            return None
        return self.repo.update_status(db, request, status)

    def get_transcript(self, db: Session, request_id: str):
        return self.repo.get_transcript(db, request_id)

    def upsert_transcript(
        self, db: Session, request_id: str, source: str, raw_text: str, cleaned_text: str | None
    ):
        transcript = self.repo.get_transcript(db, request_id)
        if transcript:
            return self.repo.update_transcript(db, transcript, raw_text, cleaned_text)
        return self.repo.create_transcript(db, request_id, source, raw_text, cleaned_text)
