from agents.app.models.ad_campaign_models import AdCampaignBrief, AdCampaignDraft, AdCreative


async def run_ad_campaign_workflow(brief: AdCampaignBrief) -> AdCampaignDraft:
    """Stub implementation of an ad campaign agent workflow.

    Replace with real Strands Agents integration; this is just a placeholder
    that returns a single creative.
    """

    creative = AdCreative(
        platform="meta",
        headline=f"{brief.product_name} for {brief.target_audience}",
        body="[stubbed ad body]",
        call_to_action="Learn more",
    )
    return AdCampaignDraft(creatives=[creative])
