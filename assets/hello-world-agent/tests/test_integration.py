"""Integration test: end-to-end agent flow with mocked LLM and external systems."""

from __future__ import annotations

import sys
import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Stub out SDK sub-modules not present in the test venv
def _stub_missing_modules():
    if "sap_cloud_sdk.agent_memory.factory" not in sys.modules:
        factory_pkg = types.ModuleType("sap_cloud_sdk.agent_memory.factory")
        factory_pkg.__path__ = []
        checkpoint_mod = types.ModuleType("sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint")
        checkpoint_mod.create_checkpointer = MagicMock(return_value=MagicMock())
        factory_pkg.langgraph_checkpoint = checkpoint_mod
        sys.modules["sap_cloud_sdk.agent_memory.factory"] = factory_pkg
        sys.modules["sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint"] = checkpoint_mod

_stub_missing_modules()


@pytest.mark.asyncio
async def test_end_to_end_greeting_flow(add_agent_to_path):
    """Full agent invoke flow: greeting message → completed response with content."""
    response_msg = MagicMock()
    response_msg.content = "Hello! I'm the Hello World Agent, here to demonstrate the A2A runtime!"
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value={"messages": [response_msg]})

    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=mock_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="integration-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        result = await agent.invoke("Hi there!", "integration-context-1")

    assert result.status == "completed"
    assert result.message, "Expected a non-empty response message"
    # Milestone M2 and M3 would have been logged; we validate the response object
    assert isinstance(result.message, str)


@pytest.mark.asyncio
async def test_end_to_end_no_tools_flow(add_agent_to_path):
    """Agent works correctly with no tools — no MCP integration required."""
    response_msg = MagicMock()
    response_msg.content = "Sure! I can greet you and answer basic questions."
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value={"messages": [response_msg]})

    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=mock_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="integration-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        # Pass no tools — agent should still work (Hello World has no MCP integrations)
        result = await agent.invoke("What can you help with?", "integration-context-2", tools=[])

    assert result.status == "completed"
    assert len(result.message) > 0
