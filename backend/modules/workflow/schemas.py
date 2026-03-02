from pydantic import BaseModel


class WorkflowCreate(BaseModel):
    transcript_request_id: str
