from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.jobs import router as jobs_router
from app.config import settings
from app.db.session import init_db
from app.schemas.health import HealthResponse


def create_app(*, initialize_db: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if initialize_db:
            init_db()
        yield

    application = FastAPI(
        title=settings.app_name,
        description="Personal job-hunting operating system API.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(jobs_router)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return application


app = create_app()
