from typing import List, Optional
from pydantic import BaseModel


class SectionCopySchema(BaseModel):
    id: str
    title: str
    body: str
    call_to_action: Optional[str] = None


class LandingPageDraftSchema(BaseModel):
    hero_headline: str
    hero_subheadline: str
    sections: List[SectionCopySchema]
    notes: Optional[str] = None


class QAEvaluationSchema(BaseModel):
    overall_score: float
    brand_voice_score: float
    clarity_score: float
    structure_score: float
    issues: List[str]
    suggestions: List[str]


class ProductionLandingPageSchema(BaseModel):
    project_id: str
    draft: LandingPageDraftSchema
    qa: QAEvaluationSchema
    approved_by_user_id: Optional[str] = None
    sentinel_status: str
    sentinel_event_ids: List[str] = []


class LandingPageRequestSchema(BaseModel):
    client_id: str
    tenant_id: str
    project_id: str
    policy_id: str
    brief_text: str
    approved_by_user_id: Optional[str] = None
