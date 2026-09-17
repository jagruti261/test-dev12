"""Tests for mcp_providers/agw.py utility functions."""
from __future__ import annotations

import sys
import types
import pytest
from unittest.mock import MagicMock

def _stub():
    if "sap_cloud_sdk.agent_memory.factory" not in sys.modules:
        factory_pkg = types.ModuleType("sap_cloud_sdk.agent_memory.factory")
        factory_pkg.__path__ = []
        checkpoint_mod = types.ModuleType("sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint")
        checkpoint_mod.create_checkpointer = MagicMock(return_value=MagicMock())
        factory_pkg.langgraph_checkpoint = checkpoint_mod
        sys.modules["sap_cloud_sdk.agent_memory.factory"] = factory_pkg
        sys.modules["sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint"] = checkpoint_mod
_stub()


@pytest.fixture
def agw(add_agent_to_path):
    from mcp_providers import agw
    return agw


def test_set_and_get_user_token(agw):
    """set_user_token stores a token retrievable via get_user_token."""
    token_ctx = agw.set_user_token("test-token-123")
    assert agw.get_user_token() == "test-token-123"
    agw.reset_user_token(token_ctx)


def test_get_user_token_default_is_none(agw):
    """get_user_token returns None when no token has been set."""
    # Reset to clean state
    ctx = agw.set_user_token(None)
    result = agw.get_user_token()
    assert result is None
    agw.reset_user_token(ctx)


def test_reset_user_token(agw):
    """reset_user_token restores previous token context."""
    ctx1 = agw.set_user_token("first-token")
    ctx2 = agw.set_user_token("second-token")
    assert agw.get_user_token() == "second-token"
    agw.reset_user_token(ctx2)
    assert agw.get_user_token() == "first-token"
    agw.reset_user_token(ctx1)


def test_build_mock_tools_missing_file(agw, tmp_path, monkeypatch):
    """_build_mock_tools returns empty list when mcp-mock.json is absent."""
    monkeypatch.setattr(agw, "_MOCK_FILE", tmp_path / "nonexistent.json")
    result = agw._build_mock_tools()
    assert result == []


def test_build_mock_tools_invalid_json(agw, tmp_path, monkeypatch):
    """_build_mock_tools returns empty list when mcp-mock.json is malformed."""
    bad_file = tmp_path / "mcp-mock.json"
    bad_file.write_text("{ invalid json }")
    monkeypatch.setattr(agw, "_MOCK_FILE", bad_file)
    result = agw._build_mock_tools()
    assert result == []


def test_build_mock_tools_empty_tools(agw, tmp_path, monkeypatch):
    """_build_mock_tools handles valid JSON with empty tools list."""
    mock_file = tmp_path / "mcp-mock.json"
    mock_file.write_text('{"tools": []}')
    monkeypatch.setattr(agw, "_MOCK_FILE", mock_file)
    result = agw._build_mock_tools()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_mcp_tools_returns_empty_in_test_mode(agw, tmp_path, monkeypatch):
    """get_mcp_tools returns empty list in IBD_TESTING mode when no mock file exists."""
    monkeypatch.setattr(agw, "_MOCK_FILE", tmp_path / "nonexistent.json")
    # IBD_TESTING=1 is set by conftest.py
    result = await agw.get_mcp_tools()
    assert isinstance(result, list)
    assert result == []


def test_get_user_sub_in_testing_mode_no_token(agw):
    """get_user_sub returns 'unknown' in IBD_TESTING mode when no token is set."""
    ctx = agw.set_user_token(None)
    try:
        sub = agw.get_user_sub()
        assert sub == "unknown"
    finally:
        agw.reset_user_token(ctx)


def test_build_mock_tools_with_server_tools(agw, tmp_path, monkeypatch):
    """_build_mock_tools creates StructuredTool instances from valid server/tool definitions."""
    import json
    mock_file = tmp_path / "mcp-mock.json"
    mock_data = {
        "servers": {
            "my-server": {
                "tools": {
                    "greet": {
                        "description": "Say hello",
                        "mock_response": {"greeting": "Hello!"},
                        "input_schema": {
                            "properties": {"name": {"type": "string", "description": "Name to greet"}},
                            "required": ["name"]
                        }
                    }
                }
            }
        }
    }
    mock_file.write_text(json.dumps(mock_data))
    monkeypatch.setattr(agw, "_MOCK_FILE", mock_file)
    result = agw._build_mock_tools()
    assert len(result) == 1
    assert result[0].name == "greet"
