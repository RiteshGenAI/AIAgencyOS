import json

from agents.app.llm_router import generate
from agents.app.models.ad_campaign_models import AdCampaignBrief, AdCampaignDraft, AdCreative
from agents.app.strands.tools.sentinel_tool_wrapper import sentinel_scan, SentinelScanInput


async def run_ad_campaign_agent(brief: AdCampaignBrief, policy_id: str) -> AdCampaignDraft:
    scan = await sentinel_scan(
        SentinelScanInput(
            payload=brief.product_description,
            policy_id=policy_id,
            scan_type="prompt",
        )
    )
    if not scan.allowed:
        raise ValueError("Ad brief blocked by Sentinel")

    system_prompt = (
        "You are a performance marketing copywriter. "
        "Return only JSON with key 'creatives' containing a list of "
        "{platform, headline, body, call_to_action} objects."
    )
    user_prompt = (
        f"Product: {brief.product_name}\n"
        f"Description: {brief.product_description}\n"
        f"Audience: {brief.target_audience}\n"
        f"Goal: {brief.primary_goal}"
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

    creatives = [AdCreative(**c) for c in data.get("creatives", [])]
    if not creatives:
        creatives = [
            AdCreative(
                platform="meta",
                headline=f"{brief.product_name} for {brief.target_audience}",
                body="[stubbed ad body]",
                call_to_action="Learn more",
            )
        ]

    return AdCampaignDraft(creatives=creatives)
