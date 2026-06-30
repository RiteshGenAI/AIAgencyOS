from agents.app.models.ad_campaign_models import AdCampaignBrief, AdCampaignDraft
from agents.app.strands.workflows.ad_campaign.agent import run_ad_campaign_agent


async def generate_ad_campaign(brief: AdCampaignBrief, policy_id: str) -> AdCampaignDraft:
    return await run_ad_campaign_agent(brief, policy_id)
