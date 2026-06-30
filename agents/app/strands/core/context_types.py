from typing import Any, Dict, Optional
from pydantic import BaseModel

from agents.app.models.landing_page_models import (
    Brief,
    ResearchSummary,
    LandingPageDraft,
    QAEvaluation,
)


class WorkflowContext(BaseModel):
    """Shared context that flows through the landing-page workflow graph."""

    brief: Optional[Brief] = None
    research: Optional[ResearchSummary] = None
    draft: Optional[LandingPageDraft] = None
    qa: Optional[QAEvaluation] = None
    metadata: Dict[str, Any] = {}
