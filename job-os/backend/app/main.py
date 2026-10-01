from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.jobs import router as jobs_router
from app.api.profile import router as profile_router
from app.api.requirements import router as requirements_router
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
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(jobs_router)
    application.include_router(profile_router)
    application.include_router(requirements_router)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return application


app = create_app()
