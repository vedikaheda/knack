from fastapi import FastAPI
from .core.logging import configure_logging
from .api.v1.router import api_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Transcript-Link BRD Agent", version="v1.1")
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


app = create_app()
