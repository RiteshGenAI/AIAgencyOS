import json

from agents.app.llm_router import generate
from agents.app.models.landing_page_models import LandingPageDraft, SectionCopy
from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.tools.sentinel_tool_wrapper import sentinel_scan, SentinelScanInput


async def run_draft_agent(ctx: WorkflowContext, policy_id: str) -> WorkflowContext:
    if not ctx.brief or not ctx.research:
        raise ValueError("Brief and research are required before drafting")

    system_prompt = (
        "You are a senior conversion copywriter. "
        "Write a landing page in JSON with exactly these keys: "
        "hero_headline (string), hero_subheadline (string), "
        "sections (list of {id, title, body, call_to_action}), "
        "notes (string). Return only valid JSON."
    )
    user_prompt = (
        f"Product: {ctx.brief.product_name or 'Unknown'}\n"
        f"Description: {ctx.brief.product_description}\n"
        f"Audience: {ctx.brief.target_audience}\n"
        f"Goal: {ctx.brief.primary_goal}\n"
        f"Tone: {ctx.brief.tone_of_voice}\n"
        f"Research notes: {ctx.research.raw_notes}"
    )

    raw = generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    sections = [
        SectionCopy(**s) for s in data.get("sections", [])
    ]
    draft = LandingPageDraft(
        hero_headline=data.get("hero_headline", ""),
        hero_subheadline=data.get("hero_subheadline", ""),
        sections=sections,
        notes=data.get("notes", ""),
    )

    payload = "\n".join(
        [draft.hero_headline, draft.hero_subheadline]
        + [s.body for s in draft.sections]
    )
    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=payload,
            policy_id=policy_id,
            scan_type="output",
        )
    )
    ctx.metadata["sentinel_draft_scan"] = scan_result.model_dump()
    ctx.draft = draft
    return ctx
