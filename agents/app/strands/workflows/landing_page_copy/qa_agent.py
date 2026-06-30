import json

from agents.app.llm_router import generate
from agents.app.models.landing_page_models import QAEvaluation
from agents.app.strands.core.context_types import WorkflowContext


async def run_qa_agent(ctx: WorkflowContext) -> WorkflowContext:
    if not ctx.draft or not ctx.brief:
        raise ValueError("Draft and brief are required for QA")

    system_prompt = (
        "You are a strict landing-page QA reviewer. "
        "Return only JSON with keys: overall_score, brand_voice_score, "
        "clarity_score, structure_score (all 0.0-1.0 floats), "
        "issues (list of strings), suggestions (list of strings)."
    )
    user_prompt = (
        f"Brief: {ctx.brief.product_description}\n"
        f"Hero: {ctx.draft.hero_headline}\n"
        f"Subhead: {ctx.draft.hero_subheadline}\n"
        f"Sections:\n"
        + "\n".join(f"- {s.title}: {s.body}" for s in ctx.draft.sections)
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
        raise ValueError(f"LLM QA returned invalid JSON: {exc}") from exc

    ctx.qa = QAEvaluation(
        overall_score=float(data.get("overall_score", 0.0)),
        brand_voice_score=float(data.get("brand_voice_score", 0.0)),
        clarity_score=float(data.get("clarity_score", 0.0)),
        structure_score=float(data.get("structure_score", 0.0)),
        issues=data.get("issues", []),
        suggestions=data.get("suggestions", []),
    )
    return ctx
