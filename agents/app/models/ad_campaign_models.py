from typing import List
from pydantic import BaseModel


class AdCampaignBrief(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    primary_goal: str  # awareness | clicks | conversions


class AdCreative(BaseModel):
    platform: str  # e.g. meta | google | linkedin
    headline: str
    body: str
    call_to_action: str


class AdCampaignDraft(BaseModel):
    creatives: List[AdCreative]
