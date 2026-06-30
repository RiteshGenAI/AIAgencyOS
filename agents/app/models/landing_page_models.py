from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class Brief(BaseModel):
    client_id: str
    project_id: str
    product_name: str
    product_description: str
    target_audience: str
    primary_goal: str  # e.g. "signups", "demo requests"
    tone_of_voice: str
    brand_guideline_urls: List[HttpUrl] = []
    reference_pages: List[HttpUrl] = []


class ResearchSummary(BaseModel):
    key_benefits: List[str]
    competitors: List[str]
    unique_selling_points: List[str]
    audience_insights: List[str]
    raw_notes: str


class SectionCopy(BaseModel):
    id: str
    title: str
    body: str
    call_to_action: Optional[str] = None


class LandingPageDraft(BaseModel):
    hero_headline: str
    hero_subheadline: str
    sections: List[SectionCopy]
    notes: Optional[str] = None


class QAEvaluation(BaseModel):
    overall_score: float
    brand_voice_score: float
    clarity_score: float
    structure_score: float
    issues: List[str]
    suggestions: List[str]


class ProductionLandingPage(BaseModel):
    project_id: str
    draft: LandingPageDraft
    qa: QAEvaluation
    approved_by_user_id: Optional[str] = None
    sentinel_status: str  # "passed" | "flagged" | "blocked"
    sentinel_event_ids: List[str] = []
