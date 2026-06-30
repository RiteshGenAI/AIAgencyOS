from pydantic import BaseModel

from agents.app.models.landing_page_models import Brief
from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.tools.sentinel_tool_wrapper import (
    sentinel_scan,
    SentinelScanInput,
)


class BriefAgentInput(BaseModel):
    raw_text: str
    client_id: str
    project_id: str
    policy_id: str


async def run_brief_agent(ctx: WorkflowContext, input: BriefAgentInput) -> WorkflowContext:
    """Normalize a raw client brief into structured fields.

    Sentinel is applied on the raw text before using it downstream.
    """

    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=input.raw_text,
            policy_id=input.policy_id,
            scan_type="prompt",
        )
    )
    ctx.metadata["sentinel_brief_scan"] = scan_result.model_dump()

    if not scan_result.allowed:
        raise ValueError("Brief blocked by Sentinel policy")

    # TODO: call Strands LLM to extract more precise fields
    brief = Brief(
        client_id=input.client_id,
        project_id=input.project_id,
        product_name="",
        product_description=input.raw_text,
        target_audience="",
        primary_goal="",
        tone_of_voice="",
    )
    ctx.brief = brief
    return ctx
