from fastapi import APIRouter
from . import auth, documents, workflows, transcript_requests, jobs, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transcript_requests.router, prefix="/transcript_requests", tags=["transcript_requests"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
