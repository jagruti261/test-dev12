"""Unit tests for the Hello World Agent."""

from __future__ import annotations

import sys
import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Stub out SDK sub-modules not present in the test venv
def _stub_missing_modules():
    """Create minimal stubs for SDK modules absent in the test venv."""
    # sap_cloud_sdk.agent_memory.factory  (hierarchy: package + submodule)
    if "sap_cloud_sdk.agent_memory.factory" not in sys.modules:
        factory_pkg = types.ModuleType("sap_cloud_sdk.agent_memory.factory")
        factory_pkg.__path__ = []  # make it look like a package
        checkpoint_mod = types.ModuleType("sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint")
        checkpoint_mod.create_checkpointer = MagicMock(return_value=MagicMock())
        factory_pkg.langgraph_checkpoint = checkpoint_mod
        sys.modules["sap_cloud_sdk.agent_memory.factory"] = factory_pkg
        sys.modules["sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint"] = checkpoint_mod

_stub_missing_modules()


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response message."""
    msg = MagicMock()
    msg.content = "Hello! I'm the Hello World Agent. How can I help you today?"
    return msg


@pytest.fixture
def mock_graph(mock_llm_response):
    """Create a mock LangGraph compiled graph."""
    graph = AsyncMock()
    graph.ainvoke = AsyncMock(return_value={"messages": [mock_llm_response]})
    return graph


@pytest.mark.asyncio
async def test_agent_greeting_response(add_agent_to_path, mock_graph):
    """Agent returns a greeting string when given an opening message."""
    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=mock_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="test-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        response = await agent.invoke("Hello!", "test-context-1")
        assert response.status == "completed"
        assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_followup_response(add_agent_to_path, mock_graph):
    """Agent handles follow-up messages and returns a non-empty response."""
    followup_msg = MagicMock()
    followup_msg.content = "I can help you with testing!"
    followup_graph = AsyncMock()
    followup_graph.ainvoke = AsyncMock(return_value={"messages": [followup_msg]})

    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=followup_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="test-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        response = await agent.invoke("What can you do?", "test-context-2")
        assert response.status == "completed"
        assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_stream_yields_processing_then_complete(add_agent_to_path, mock_graph):
    """stream() yields a 'Processing...' chunk followed by a completed chunk."""
    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=mock_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="test-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        chunks = []
        async for chunk in agent.stream("Hello!", "test-context-3"):
            chunks.append(chunk)

        assert len(chunks) >= 2
        # First chunk is the processing indicator
        assert chunks[0]["is_task_complete"] is False
        # Last chunk is the final response
        assert chunks[-1]["is_task_complete"] is True
        assert len(chunks[-1]["content"]) > 0


@pytest.mark.asyncio
async def test_agent_handles_error_gracefully(add_agent_to_path):
    """Agent returns an error status gracefully when LLM call fails."""
    error_graph = AsyncMock()
    error_graph.ainvoke = AsyncMock(side_effect=Exception("LLM unavailable"))

    with patch("agent.ChatLiteLLM"), \
         patch("agent.create_agent", return_value=error_graph), \
         patch("agent.create_checkpointer", return_value=MagicMock()), \
         patch("agent.SummarizationMiddleware", return_value=MagicMock()), \
         patch("agent.get_user_sub", return_value="test-user"):
        from agent import SampleAgent
        agent = SampleAgent()
        response = await agent.invoke("Hello!", "test-context-error")
        # Should not raise — returns completed with error message
        assert response.status in ("completed", "error")
        assert len(response.message) > 0
