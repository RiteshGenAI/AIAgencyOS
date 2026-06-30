import json
import unittest
from unittest.mock import patch, AsyncMock

from agents.app.models.ad_campaign_models import AdCampaignBrief
from agents.app.models.landing_page_models import Brief, ResearchSummary
from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.tools.sentinel_tool_wrapper import SentinelScanResult
from agents.app.strands.workflows.landing_page_copy.draft_agent import run_draft_agent
from agents.app.strands.workflows.landing_page_copy.qa_agent import run_qa_agent
from agents.app.strands.workflows.ad_campaign.agent import run_ad_campaign_agent


class TestWorkflowAgents(unittest.TestCase):
    def _make_brief(self):
        return Brief(
            client_id="client-1",
            project_id="project-1",
            product_name="TestProduct",
            product_description="A tool for testing.",
            target_audience="Developers",
            primary_goal="signups",
            tone_of_voice="professional",
            brand_guideline_urls=[],
            reference_pages=[],
        )

    def _make_research(self):
        return ResearchSummary(
            key_benefits=[],
            competitors=[],
            unique_selling_points=[],
            audience_insights=[],
            raw_notes="raw notes",
        )

    @patch("agents.app.strands.workflows.landing_page_copy.draft_agent.generate")
    @patch("agents.app.strands.workflows.landing_page_copy.draft_agent.sentinel_scan", new_callable=AsyncMock)
    async def _run_draft(self, mock_generate, mock_sentinel):
        mock_generate.return_value = json.dumps({
            "hero_headline": "Headline",
            "hero_subheadline": "Subheadline",
            "sections": [
                {"id": "hero", "title": "Hero", "body": "Hero body", "call_to_action": "Go"},
            ],
            "notes": "notes",
        })
        mock_sentinel.return_value = SentinelScanResult(
            allowed=True,
            risk_score=0.1,
            issues=[],
            event_id="evt-1",
        )
        ctx = WorkflowContext(
            brief=self._make_brief(),
            research=self._make_research(),
        )
        result = await run_draft_agent(ctx, policy_id="policy-1")
        return result, mock_generate, mock_sentinel

    def test_draft_agent(self):
        result, mock_generate, mock_sentinel = self.run_async(self._run_draft)
        self.assertIsNotNone(result.draft)
        self.assertEqual(result.draft.hero_headline, "Headline")
        self.assertEqual(len(result.draft.sections), 1)
        self.assertEqual(result.metadata["sentinel_draft_scan"]["allowed"], True)
        mock_generate.assert_called_once()
        mock_sentinel.assert_awaited_once()

    @patch("agents.app.strands.workflows.landing_page_copy.qa_agent.generate")
    async def _run_qa(self, mock_generate):
        mock_generate.return_value = json.dumps({
            "overall_score": 0.9,
            "brand_voice_score": 0.8,
            "clarity_score": 0.85,
            "structure_score": 0.88,
            "issues": ["generic"],
            "suggestions": ["be specific"],
        })
        ctx = WorkflowContext(
            brief=self._make_brief(),
            draft=result.draft,
        )
        return await run_qa_agent(ctx)

    def test_qa_agent(self):
        draft_ctx, _, _ = self.run_async(self._run_draft)
        self._run_qa.__self__ = self  # not needed, helper below uses closure differently
        # Re-run with explicit helper to avoid method self confusion.
        qa_ctx = self.run_async(self._run_qa_with_draft, draft_ctx.draft)
        self.assertIsNotNone(qa_ctx.qa)
        self.assertEqual(qa_ctx.qa.overall_score, 0.9)
        self.assertEqual(qa_ctx.qa.issues, ["generic"])

    @patch("agents.app.strands.workflows.landing_page_copy.qa_agent.generate")
    async def _run_qa_with_draft(self, draft, mock_generate):
        mock_generate.return_value = json.dumps({
            "overall_score": 0.9,
            "brand_voice_score": 0.8,
            "clarity_score": 0.85,
            "structure_score": 0.88,
            "issues": ["generic"],
            "suggestions": ["be specific"],
        })
        ctx = WorkflowContext(
            brief=self._make_brief(),
            draft=draft,
        )
        return await run_qa_agent(ctx)

    @patch("agents.app.strands.workflows.ad_campaign.agent.generate")
    @patch("agents.app.strands.workflows.ad_campaign.agent.sentinel_scan", new_callable=AsyncMock)
    async def _run_ad(self, mock_generate, mock_sentinel):
        mock_generate.return_value = json.dumps({
            "creatives": [
                {
                    "platform": "meta",
                    "headline": "H",
                    "body": "B",
                    "call_to_action": "Go",
                }
            ]
        })
        mock_sentinel.return_value = SentinelScanResult(
            allowed=True,
            risk_score=0.0,
            issues=[],
            event_id="evt-2",
        )
        brief = AdCampaignBrief(
            product_name="TestProduct",
            product_description="A tool for testing.",
            target_audience="Developers",
            primary_goal="conversions",
        )
        return await run_ad_campaign_agent(brief, policy_id="policy-2")

    def test_ad_campaign_agent(self):
        draft = self.run_async(self._run_ad)
        self.assertEqual(len(draft.creatives), 1)
        self.assertEqual(draft.creatives[0].platform, "meta")

    @patch("agents.app.strands.workflows.ad_campaign.agent.sentinel_scan", new_callable=AsyncMock)
    async def _run_ad_blocked(self, mock_sentinel):
        mock_sentinel.return_value = SentinelScanResult(
            allowed=False,
            risk_score=1.0,
            issues=["blocked"],
            event_id="evt-3",
        )
        brief = AdCampaignBrief(
            product_name="TestProduct",
            product_description="Bad",
            target_audience="Developers",
            primary_goal="conversions",
        )
        return await run_ad_campaign_agent(brief, policy_id="policy-3")

    def test_ad_campaign_blocked(self):
        with self.assertRaises(ValueError) as ctx:
            self.run_async(self._run_ad_blocked)
        self.assertIn("blocked by Sentinel", str(ctx.exception))

    def run_async(self, coro, *args):
        import asyncio
        return asyncio.run(coro(self, *args) if args else coro(self))


if __name__ == "__main__":
    unittest.main()
