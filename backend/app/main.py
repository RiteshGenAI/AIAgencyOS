from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, CorrelationIdMiddleware
from backend.app.core.middleware import (
    ErrorHandlingMiddleware,
    RateLimitingMiddleware,
    RequestLoggingMiddleware,
)
from backend.app.db.init_db import init_db
from backend.app.db.seed import seed_admin_user
from backend.app.api.v1.workflows import router as workflows_router
from backend.app.api.v1.leads import router as leads_router
from backend.app.api.v1.projects import router as projects_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.sentinel_events import router as sentinel_events_router
from backend.app.api.v1.invoices import router as invoices_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.clients import router as clients_router
from backend.app.api.internal.sentinel import router as internal_sentinel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_admin_user()
    yield


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(workflows_router, prefix=settings.API_V1_STR)
    app.include_router(leads_router, prefix=settings.API_V1_STR)
    app.include_router(projects_router, prefix=settings.API_V1_STR)
    app.include_router(sentinel_events_router, prefix=settings.API_V1_STR)
    app.include_router(invoices_router, prefix=settings.API_V1_STR)
    app.include_router(health_router, prefix=settings.API_V1_STR)
    app.include_router(admin_router, prefix=settings.API_V1_STR)
    app.include_router(clients_router, prefix=settings.API_V1_STR)
    app.include_router(internal_sentinel_router)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
