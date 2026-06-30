from typing import List
from pydantic import BaseModel


class WebResearchInput(BaseModel):
    query: str
    max_results: int = 10


class WebResearchOutput(BaseModel):
    snippets: List[str]


def web_research_tool(input: WebResearchInput) -> WebResearchOutput:
    """Placeholder web research tool.

    In production, integrate Tavily or another search API and return text snippets
    for downstream reasoning.
    """

    # TODO: implement real search integration
    return WebResearchOutput(snippets=[f"[stubbed search result for '{input.query}']"])
