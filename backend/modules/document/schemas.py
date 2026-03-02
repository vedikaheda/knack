from pydantic import BaseModel


class DocumentCreate(BaseModel):
    transcript_request_id: str
    google_doc_id: str
    doc_type: str = "BRD"
