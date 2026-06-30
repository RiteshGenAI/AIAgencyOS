"""Landing page workflow agent using Strands-style definitions.

This is a structural stub so you can plug in the real Strands SDK types.
"""

from agents.app.models.landing_page_models import (
    Brief,
    ResearchSummary,
    LandingPageDraft,
    QAEvaluation,
    ProductionLandingPage,
)
from agents.app.strands.tools.web_research_tool import WebResearchInput, web_research_tool
from agents.app.strands.tools.sentinel_tool_wrapper import sentinel_scan, SentinelScanInput


async def run_landing_page_agent(
    brief_text: str,
    client_id: str,
    project_id: str,
    policy_id: str,
    approved_by_user_id: str | None = None,
) -> ProductionLandingPage:
    """High-level orchestration using Strands-style steps.

    In real Strands code, you would:
    - Create an Agent with a model config (Bedrock/Claude)
    - Register tools (web research, Sentinel, persistence)
    - Use an AgentRunner / workflow graph to execute steps
    Here we keep the same semantics but as simple async functions.
    """

    # 1) Brief normalization + Sentinel scan
    brief_scan = await sentinel_scan(
        SentinelScanInput(payload=brief_text, policy_id=policy_id, scan_type="prompt")
    )

    if not brief_scan.allowed:
        raise ValueError("Brief blocked by Sentinel policy")

    brief = Brief(
        client_id=client_id,
        project_id=project_id,
        product_name="",
        product_description=brief_text,
        target_audience="",
        primary_goal="",
        tone_of_voice="",
    )

    # 2) Research step
    query = f"{brief.product_name} {brief.product_description} benefits competitors"
    research_result = web_research_tool(WebResearchInput(query=query, max_results=8))
    notes = "
".join(research_result.snippets)

    research_scan = await sentinel_scan(
        SentinelScanInput(payload=notes, policy_id=policy_id, scan_type="output")
    )

    research = ResearchSummary(
        key_benefits=[],
        competitors=[],
        unique_selling_points=[],
        audience_insights=[],
        raw_notes=notes,
    )

    # 3) Draft step (replace with real Strands LLM call)
    sections = []
    sections.append(
        LandingPageDraft.model_fields['sections'].annotation.__args__[0](  # type: ignore
            id="hero",
            title="Hero Section",
            body="[stubbed hero body]",
            call_to_action="Get started",
        )
    )

    draft = LandingPageDraft(
        hero_headline="Amazing Product for Busy Teams",
        hero_subheadline="Ship better campaigns with AI-native workflows.",
        sections=sections,
        notes="",
    )

    draft_payload = (
        draft.hero_headline
        + "
"
        + draft.hero_subheadline
        + "
"
        + "
".join(s.body for s in draft.sections)
    )

    draft_scan = await sentinel_scan(
        SentinelScanInput(payload=draft_payload, policy_id=policy_id, scan_type="output")
    )

    # 4) QA step (stub)
    qa = QAEvaluation(
        overall_score=0.85,
        brand_voice_score=0.8,
        clarity_score=0.9,
        structure_score=0.8,
        issues=["Headline may be too generic"],
        suggestions=["Add a more specific benefit in the hero headline."],
    )

    sentinel_status = "passed"
    sentinel_event_ids: list[str] = []
    for result in (brief_scan, research_scan, draft_scan):
        if not result.allowed:
            sentinel_status = "flagged"
        sentinel_event_ids.append(result.event_id)

    return ProductionLandingPage(
        project_id=project_id,
        draft=draft,
        qa=qa,
        approved_by_user_id=approved_by_user_id,
        sentinel_status=sentinel_status,
        sentinel_event_ids=sentinel_event_ids,
    )
