from pydantic import BaseModel


class TranscriptRequestCreate(BaseModel):
    source_link: str

