import uuid
from typing import Literal

import httpx
from pydantic import BaseModel

from backend.app.core.config import settings


class SentinelScanInput(BaseModel):
    payload: str
    policy_id: str
    scan_type: Literal["prompt", "output", "tool_call"]


class SentinelScanResult(BaseModel):
    allowed: bool
    risk_score: float
    issues: list[str]
    event_id: str


def _local_allow_result() -> SentinelScanResult:
    return SentinelScanResult(
        allowed=True,
        risk_score=0.0,
        issues=[],
        event_id=str(uuid.uuid4()),
    )


async def sentinel_scan(input: SentinelScanInput) -> SentinelScanResult:
    if not settings.SENTINEL_PROXY_ENABLED:
        return _local_allow_result()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.SENTINEL_URL}/scan",
                json=input.model_dump(),
            )
            resp.raise_for_status()
            data = resp.json()
        return SentinelScanResult(**data)
    except Exception:
        if settings.ENV == "local":
            return _local_allow_result()
        raise
