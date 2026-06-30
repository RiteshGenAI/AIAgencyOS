import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from agents.app.models.landing_page_models import ProductionLandingPage
from agents.app.services.landing_page_runner import generate_landing_page_copy
from agents.app.models.ad_campaign_models import AdCampaignBrief, AdCampaignDraft
from agents.app.services.ad_campaign_runner import generate_ad_campaign


app = FastAPI(title="Agents Service")


class LandingPageRequest(BaseModel):
    client_id: str
    project_id: str
    policy_id: str
    brief_text: str
    approved_by_user_id: str | None = None


class AdCampaignRequest(BaseModel):
    brief: AdCampaignBrief
    policy_id: str


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agents/landing-page", response_model=ProductionLandingPage)
async def run_landing_page_agent(req: LandingPageRequest) -> ProductionLandingPage:
    return await generate_landing_page_copy(
        brief_text=req.brief_text,
        client_id=req.client_id,
        project_id=req.project_id,
        policy_id=req.policy_id,
        approved_by_user_id=req.approved_by_user_id,
    )


@app.post("/agents/ad-campaign", response_model=AdCampaignDraft)
async def run_ad_campaign_agent(req: AdCampaignRequest) -> AdCampaignDraft:
    return await generate_ad_campaign(req.brief, req.policy_id)


if __name__ == "__main__":
    uvicorn.run("agents.app.main:app", host="0.0.0.0", port=8081, reload=True)
