"""Integration and configuration tests for Google ADK customer_support_agent."""

import pytest
from app.agent import customer_support_agent, root_agent
from app.runner import CustomerSupportRunner
from google.adk.cli.utils.agent_loader import AgentLoader


class TestAgentConfiguration:
    def test_agent_attributes(self):
        assert root_agent.name == "customer_support_agent"
        assert customer_support_agent is root_agent
        assert "Nova" in root_agent.instruction
        assert len(root_agent.tools) == 4

    def test_tools_registered_by_name(self):
        tool_names = {t.__name__ for t in root_agent.tools}
        expected = {
            "get_order_status",
            "check_refund_policy",
            "create_support_ticket",
            "get_customer_account",
        }
        assert tool_names == expected

    def test_adk_cli_loader_discovery(self):
        loader = AgentLoader(".")
        agents = loader.list_agents()
        assert "app" in agents

        loaded = loader.load_agent("app")
        assert loaded.name == "customer_support_agent"


class TestRunnerBehavior:
    def test_runner_initialization(self):
        runner = CustomerSupportRunner(agent=root_agent)
        assert runner.agent.name == "customer_support_agent"

    def test_runner_missing_api_key_handling(self, monkeypatch):
        # Force missing key
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        runner = CustomerSupportRunner(agent=root_agent)
        response = runner.ask_sync("Where is order ORD-1001?")
        assert "[Configuration Notice]" in response.text
        assert "GOOGLE_API_KEY" in response.text

    def test_session_lifecycle(self, monkeypatch):
        import asyncio

        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        runner = CustomerSupportRunner(agent=root_agent)

        async def run_lifecycle():
            # Ensure session can be created and deleted cleanly
            await runner._ensure_session(user_id="test_user", session_id="test_session")
            assert ("test_user", "test_session") in runner.active_sessions

            await runner.clear_session(user_id="test_user", session_id="test_session")
            assert ("test_user", "test_session") not in runner.active_sessions

        asyncio.run(run_lifecycle())
