"""Tests for the circuit breaker module."""
from __future__ import annotations

import sys
import types
import pytest
from unittest.mock import MagicMock

# Stub missing modules before importing anything from app/
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
def breaker(add_agent_to_path):
    from circuit_breaker import CircuitBreaker
    return CircuitBreaker(failure_threshold=2, cooldown_seconds=10.0)


@pytest.mark.asyncio
async def test_allows_initially(breaker):
    """A fresh breaker allows any model."""
    assert await breaker.allows("model-a") is True


@pytest.mark.asyncio
async def test_opens_after_threshold(breaker):
    """Breaker opens after failure_threshold consecutive failures."""
    await breaker.record_failure("model-a")
    assert await breaker.allows("model-a") is True  # not yet open
    await breaker.record_failure("model-a")
    assert await breaker.allows("model-a") is False  # now open


@pytest.mark.asyncio
async def test_success_resets_breaker(breaker):
    """Recording a success resets a model to healthy."""
    await breaker.record_failure("model-b")
    await breaker.record_success("model-b")
    assert await breaker.allows("model-b") is True


@pytest.mark.asyncio
async def test_cooldown_expires(add_agent_to_path):
    """After cooldown, the breaker transitions to half-open and allows a probe."""
    from circuit_breaker import CircuitBreaker
    current_time = [0.0]
    cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=5.0, time_fn=lambda: current_time[0])
    await cb.record_failure("model-c")
    assert await cb.allows("model-c") is False  # open
    current_time[0] = 6.0  # advance past cooldown
    assert await cb.allows("model-c") is True  # half-open, allows probe


@pytest.mark.asyncio
async def test_half_open_failure_reopens(add_agent_to_path):
    """A failure during half-open state re-opens the breaker."""
    from circuit_breaker import CircuitBreaker
    current_time = [0.0]
    cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=5.0, time_fn=lambda: current_time[0])
    await cb.record_failure("model-d")
    current_time[0] = 6.0
    await cb.allows("model-d")  # transition to half-open
    await cb.record_failure("model-d")  # fail probe → re-open
    assert await cb.allows("model-d") is False
