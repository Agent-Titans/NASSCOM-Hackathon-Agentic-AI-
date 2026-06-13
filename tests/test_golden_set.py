"""Golden-set accuracy — Use Case 1 classification, hand, and department targets (≥85%)."""
from __future__ import annotations

import pytest

from src.config.settings import get_settings
from src.db.session import get_session_factory, init_db, reset_db_caches
from tests.golden_runner import GOLDEN_PATH, load_golden_cases, run_golden_set


@pytest.fixture
def golden_db(monkeypatch, tmp_path):
    db_file = tmp_path / "golden.db"
    monkeypatch.setenv("SQLITE_DATABASE_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    reset_db_caches()
    init_db()
    Session = get_session_factory()
    with Session() as session:
        yield session
    get_settings.cache_clear()
    reset_db_caches()


def test_golden_set_file_has_minimum_cases():
    cases, thresholds = load_golden_cases()
    assert len(cases) >= 15
    assert thresholds.get("classification_accuracy", 0) >= 0.85
    categories = {c["expect"]["category"] for c in cases}
    assert categories >= {
        "Infrastructure",
        "Application",
        "Security",
        "Database",
        "Storage",
        "Network",
        "Access Management",
    }


@pytest.mark.slow
def test_golden_set_accuracy_meets_threshold(golden_db, capsys):
    """Full pipeline on golden set — jury metric: ≥85% on category, hand, department."""
    report = run_golden_set(golden_db)
    for line in report.summary_lines():
        print(line)

    assert report.total >= 15
    assert report.all_passed, "\n".join(report.summary_lines())
    assert report.meets_thresholds(), "\n".join(report.summary_lines())
