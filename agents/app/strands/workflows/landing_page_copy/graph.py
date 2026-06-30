from typing import List

from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.workflows.landing_page_copy.brief_agent import (
    run_brief_agent,
    BriefAgentInput,
)
from agents.app.strands.workflows.landing_page_copy.research_agent import (
    run_research_agent,
)
from agents.app.strands.workflows.landing_page_copy.draft_agent import (
    run_draft_agent,
)
from agents.app.strands.workflows.landing_page_copy.qa_agent import run_qa_agent
from agents.app.models.landing_page_models import ProductionLandingPage


async def run_landing_page_workflow(
    raw_brief_text: str,
    client_id: str,
    project_id: str,
    policy_id: str,
    approved_by_user_id: str | None = None,
) -> ProductionLandingPage:
    """Top-level orchestration for the landing-page-copy workflow."""

    ctx = WorkflowContext()

    ctx = await run_brief_agent(
        ctx,
        BriefAgentInput(
            raw_text=raw_brief_text,
            client_id=client_id,
            project_id=project_id,
            policy_id=policy_id,
        ),
    )

    ctx = await run_research_agent(ctx, policy_id=policy_id)
    ctx = await run_draft_agent(ctx, policy_id=policy_id)
    ctx = await run_qa_agent(ctx)

    sentinel_status = "passed"
    sentinel_event_ids: List[str] = []

    for key, value in ctx.metadata.items():
        if key.startswith("sentinel_") and isinstance(value, dict):
            event_id = value.get("event_id")
            if event_id:
                sentinel_event_ids.append(event_id)

    if sentinel_event_ids:
        sentinel_status = "flagged"

    return ProductionLandingPage(
        project_id=project_id,
        draft=ctx.draft,
        qa=ctx.qa,
        approved_by_user_id=approved_by_user_id,
        sentinel_status=sentinel_status,
        sentinel_event_ids=sentinel_event_ids,
    )
