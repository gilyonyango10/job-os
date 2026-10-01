from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.errors import (
    AIProviderError,
    AIProviderNotConfigured,
    AIResponseInvalid,
    EmptyJobDescription,
)
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
    _register_exception_handlers(application)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return application


def _register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(AIProviderNotConfigured)
    async def not_configured(
        _request: Request, exc: AIProviderNotConfigured
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @application.exception_handler(AIResponseInvalid)
    async def invalid_response(_request: Request, exc: AIResponseInvalid) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @application.exception_handler(EmptyJobDescription)
    async def empty_description(
        _request: Request, exc: EmptyJobDescription
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @application.exception_handler(AIProviderError)
    async def provider_error(_request: Request, exc: AIProviderError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})


app = create_app()
