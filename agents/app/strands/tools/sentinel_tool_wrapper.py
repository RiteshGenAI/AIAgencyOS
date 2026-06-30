from typing import Literal

import httpx
from pydantic import BaseModel

from agents.app.strands.core.config import settings


class SentinelScanInput(BaseModel):
    payload: str
    policy_id: str
    scan_type: Literal["prompt", "output", "tool_call"]


class SentinelScanResult(BaseModel):
    allowed: bool
    risk_score: float
    issues: list[str]
    event_id: str


async def sentinel_scan(input: SentinelScanInput) -> SentinelScanResult:
    """Call Sentinel scan endpoint and return the result.

    Sentinel should be exposed by the backend at /internal/sentinel/scan.
    """

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.sentinel_base_url}/scan",
            json=input.model_dump(),
        )
        resp.raise_for_status()
        data = resp.json()
    return SentinelScanResult(**data)
