from agents.app.models.landing_page_models import ResearchSummary
from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.tools.web_research_tool import (
    WebResearchInput,
    web_research_tool,
)
from agents.app.strands.tools.sentinel_tool_wrapper import (
    sentinel_scan,
    SentinelScanInput,
)


async def run_research_agent(ctx: WorkflowContext, policy_id: str) -> WorkflowContext:
    """Perform lightweight web research around the product and audience."""

    if not ctx.brief:
        raise ValueError("Brief is required before research")

    query = f"{ctx.brief.product_name} {ctx.brief.product_description} benefits competitors"
    web_result = web_research_tool(WebResearchInput(query=query, max_results=8))

    notes = "
".join(web_result.snippets)

    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=notes,
            policy_id=policy_id,
            scan_type="output",
        )
    )
    ctx.metadata["sentinel_research_scan"] = scan_result.model_dump()

    research = ResearchSummary(
        key_benefits=[],
        competitors=[],
        unique_selling_points=[],
        audience_insights=[],
        raw_notes=notes,
    )
    ctx.research = research
    return ctx
