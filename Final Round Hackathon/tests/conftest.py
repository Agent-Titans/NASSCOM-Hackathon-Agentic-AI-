"""Shared pytest helpers."""
from __future__ import annotations

import pytest

from src.config.settings import get_settings
from src.config.supervisor_policy import get_supervisor_policy


def _clear_supervisor_caches() -> None:
    get_settings.cache_clear()
    get_supervisor_policy.cache_clear()


@pytest.fixture(autouse=True)
def _reset_policy_cache():
    _clear_supervisor_caches()
    yield
    _clear_supervisor_caches()


@pytest.fixture
def strict_lld_mode(monkeypatch):
    """Switch to LLD-canonical Supervisor policy for one test."""
    monkeypatch.setenv("SUPERVISOR_MODE", "strict_lld")
    _clear_supervisor_caches()
    yield
    monkeypatch.delenv("SUPERVISOR_MODE", raising=False)
    _clear_supervisor_caches()


@pytest.fixture
def demo_mode(monkeypatch):
    """Ensure demo Supervisor policy (default) with clean cache."""
    monkeypatch.setenv("SUPERVISOR_MODE", "demo")
    _clear_supervisor_caches()
    yield
    monkeypatch.delenv("SUPERVISOR_MODE", raising=False)
    _clear_supervisor_caches()
