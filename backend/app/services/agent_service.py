import httpx

from backend.app.core.config import settings
from backend.app.schemas.landing_page_schema import (
    LandingPageRequestSchema,
    ProductionLandingPageSchema,
)


async def call_landing_page_agent(
    payload: LandingPageRequestSchema,
) -> ProductionLandingPageSchema:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.AGENTS_SERVICE_URL}/agents/landing-page",
            json=payload.model_dump(),
        )
        resp.raise_for_status()
        data = resp.json()
    return ProductionLandingPageSchema(**data)
