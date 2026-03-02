from sqlalchemy.orm import Session
from ...models.transcript_request import TranscriptRequest
from ...models.transcript import Transcript


class TranscriptRequestRepository:
    def create(self, db: Session, user_id: str, source_link: str) -> TranscriptRequest:
        request = TranscriptRequest(user_id=user_id, source_link=source_link, status="SUBMITTED")
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    def get(self, db: Session, request_id: str) -> TranscriptRequest | None:
        return db.query(TranscriptRequest).filter(TranscriptRequest.id == request_id).first()

    def list_by_user(self, db: Session, user_id: str, limit: int = 50):
        return (
            db.query(TranscriptRequest)
            .filter(TranscriptRequest.user_id == user_id)
            .order_by(TranscriptRequest.created_at.desc())
            .limit(limit)
            .all()
        )

    def update_status(self, db: Session, request: TranscriptRequest, status: str):
        request.status = status
        db.commit()
        db.refresh(request)
        return request

    def get_transcript(self, db: Session, request_id: str) -> Transcript | None:
        return (
            db.query(Transcript)
            .filter(Transcript.transcript_request_id == request_id)
            .first()
        )

    def create_transcript(
        self, db: Session, request_id: str, source: str, raw_text: str, cleaned_text: str | None
    ) -> Transcript:
        transcript = Transcript(
            transcript_request_id=request_id,
            source=source,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        return transcript

    def update_transcript(
        self, db: Session, transcript: Transcript, raw_text: str, cleaned_text: str | None
    ) -> Transcript:
        transcript.raw_text = raw_text
        transcript.cleaned_text = cleaned_text
        db.commit()
        db.refresh(transcript)
        return transcript
