from agents.app.models.landing_page_models import ProductionLandingPage
from agents.app.strands.workflows.landing_page_copy.agent import run_landing_page_agent


async def generate_landing_page_copy(
    brief_text: str,
    client_id: str,
    project_id: str,
    policy_id: str,
    approved_by_user_id: str | None = None,
) -> ProductionLandingPage:
    return await run_landing_page_agent(
        brief_text=brief_text,
        client_id=client_id,
        project_id=project_id,
        policy_id=policy_id,
        approved_by_user_id=approved_by_user_id,
    )
