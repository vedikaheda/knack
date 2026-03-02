from pydantic import BaseModel


class JobExecuteRequest(BaseModel):
    job: str
    arguments: dict
    context: dict

