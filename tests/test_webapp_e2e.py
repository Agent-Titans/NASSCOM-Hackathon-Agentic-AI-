"""
Browser E2E smoke tests — Streamlit UI + Use Case 1 flows.

Requires: playwright (`pip install playwright && playwright install chromium`)
App running: streamlit run src/ui/app.py (default :8501)
"""
from __future__ import annotations

import os
import re
import time

import pytest

BASE_URL = os.environ.get("SARATHI_E2E_URL", "http://localhost:8501")
DEMO_PASSWORD = "1234"
PIPELINE_TIMEOUT_MS = 120_000


def _require_playwright():
    pytest.importorskip("playwright.sync_api")


def _goto_signin(page):
    page.goto(BASE_URL, wait_until="networkidle", timeout=30_000)
    page.get_by_role("button", name="Sign In").first.click()
    page.wait_for_timeout(1500)


def _login(page, email: str):
    _goto_signin(page)
    page.locator('[class*="st-key-signin_email"] input').fill(email)
    page.locator('[class*="st-key-signin_password"] input').fill(DEMO_PASSWORD)
    page.locator('button[data-testid="stBaseButton-primaryFormSubmit"]').click()
    page.wait_for_timeout(2500)


def _app_up() -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen(BASE_URL, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def browser_ctx():
    _require_playwright()
    if not _app_up():
        pytest.skip(f"Streamlit not reachable at {BASE_URL}")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser_ctx):
    pg = browser_ctx.new_page()
    yield pg
    pg.close()


class TestUseCaseRequirements:
    """Use Case 1 — classify, route, suggest resolution, escalate, confidence."""

    def test_uc1_welcome_and_signin_ui(self, page):
        page.goto(BASE_URL, wait_until="networkidle", timeout=30_000)
        body = page.inner_text("body")
        assert "SAARTHI" in body
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(1000)
        assert page.locator(".signin-heading").inner_text() == "Sign In"
        assert page.locator('[class*="st-key-signin_email"]').count() == 1

    def test_uc1_employee_create_password_hand1(self, page):
        _login(page, "pallavi@user")
        assert page.get_by_role("button", name="+ New Request").count() >= 1
        page.get_by_role("button", name="+ New Request").click()
        page.wait_for_timeout(1500)

        page.get_by_label("Issue Title").fill("Forgot password")
        page.get_by_label("Description").fill(
            "I forgot my Windows password and cannot login to my laptop"
        )
        page.locator('button[data-testid="stBaseButton-primaryFormSubmit"]').click()

        page.wait_for_selector(
            "text=Self-Help",
            timeout=PIPELINE_TIMEOUT_MS,
        )
        body = page.inner_text("body")
        assert "Self-Help" in body or "Hand 1" in body
        assert page.get_by_role("button", name="Worked").count() >= 1
        assert page.get_by_role("button", name="Did not work").count() >= 1

    def test_uc1_security_escalates_hand3(self, page):
        _login(page, "gajanan@user")
        page.get_by_role("button", name="+ New Request").click()
        page.wait_for_timeout(1500)

        page.get_by_label("Issue Title").fill("VPN breach")
        page.get_by_label("Description").fill(
            "Possible security breach on VPN - unauthorized access detected on admin account"
        )
        page.locator('button[data-testid="stBaseButton-primaryFormSubmit"]').click()

        page.wait_for_function(
            """() => {
              const t = document.body.innerText;
              return t.includes('Specialist')
                || t.includes('human specialist')
                || t.includes('SecOps')
                || t.includes('Request submitted');
            }""",
            timeout=PIPELINE_TIMEOUT_MS,
        )
        if page.get_by_role("button", name="OK").count():
            page.get_by_role("button", name="OK").click()
            page.wait_for_timeout(1000)
        body = page.inner_text("body")
        assert re.search(r"Specialist|SecOps|human specialist", body, re.I)

    def test_uc1_h1_did_not_work_escalates(self, page):
        _login(page, "imran@user")
        page.get_by_role("button", name="+ New Request").click()
        page.wait_for_timeout(1500)

        page.get_by_label("Issue Title").fill("Password reset help")
        page.get_by_label("Description").fill(
            "I forgot my password and need to reset my corporate login"
        )
        page.locator('button[data-testid="stBaseButton-primaryFormSubmit"]').click()
        page.wait_for_selector("text=Did not work", timeout=PIPELINE_TIMEOUT_MS)
        page.get_by_role("button", name="Did not work").click()
        page.wait_for_timeout(4000)
        body = page.inner_text("body")
        assert re.search(r"Routed|Smart Routing|Hand 2|assigned", body, re.I)


class TestRoleWorkspaces:
    def test_agent_queue_loads(self, page):
        _login(page, "sree@employee")
        body = page.inner_text("body")
        assert re.search(r"queue|Overview|Dashboard|Team", body, re.I)

    def test_agent_queue_filters(self, page):
        _login(page, "sree@employee")
        page.wait_for_timeout(2000)
        for label in ("All", "Unassigned", "Mine", "SLA at risk"):
            page.get_by_text(label, exact=True).first.click()
            page.wait_for_timeout(800)
        body = page.inner_text("body")
        assert re.search(r"Department inbox|Queue filter", body, re.I)

    def test_admin_audit_log(self, page):
        _login(page, "admin@employee")
        page.get_by_role("button", name="Audit log").click()
        page.wait_for_timeout(2000)
        body = page.inner_text("body")
        assert re.search(r"audit|event|ticket", body, re.I)

    def test_invalid_login_rejected(self, page):
        _goto_signin(page)
        page.locator('[class*="st-key-signin_email"] input').fill("nota@user")
        page.locator('[class*="st-key-signin_password"] input').fill("wrong")
        page.locator('button[data-testid="stBaseButton-primaryFormSubmit"]').click()
        page.wait_for_timeout(2000)
        body = page.inner_text("body")
        assert re.search(r"Invalid|Unknown|required", body, re.I)
