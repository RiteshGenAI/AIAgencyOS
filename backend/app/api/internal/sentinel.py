import uuid

import httpx
from fastapi import APIRouter

from backend.app.core.config import settings
from backend.app.services.sentinel_service import (
    SentinelScanInput,
    SentinelScanResult,
)

router = APIRouter(prefix="/internal/sentinel", tags=["internal-sentinel"])


def _local_allow_result() -> SentinelScanResult:
    return SentinelScanResult(
        allowed=True,
        risk_score=0.0,
        issues=[],
        event_id=str(uuid.uuid4()),
    )


@router.post("/scan", response_model=SentinelScanResult)
async def internal_sentinel_scan(input: SentinelScanInput) -> SentinelScanResult:
    if not settings.SENTINEL_PROXY_ENABLED:
        return _local_allow_result()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.SENTINEL_URL}/scan",
                json=input.model_dump(),
            )
            resp.raise_for_status()
            return SentinelScanResult(**resp.json())
    except Exception:
        if settings.ENV == "local":
            return _local_allow_result()
        raise
