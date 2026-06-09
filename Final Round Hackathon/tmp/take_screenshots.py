"""Take screenshots of the ClearHand app for the user manual."""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.chdir(str(ROOT))
OUT = ROOT / "tmp" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def ss(page, name: str, wait_sec: float = 2.0):
    time.sleep(wait_sec)
    fp = OUT / f"{name}.png"
    page.screenshot(path=str(fp), full_page=True)
    print(f"  ✓ {name}")


def click_btn(page, text, timeout=15000):
    """Click a button by its exact visible text."""
    page.get_by_role("button", name=text, exact=True).first.click(timeout=timeout)


def click_overlay(page, idx=0, timeout=15000):
    """Click an overlay st.button('') by index."""
    page.locator("button[data-testid='stBaseButton-secondary']").nth(idx).click(force=True, timeout=timeout)


def click_primary(page, timeout=15000):
    """Click first primary button."""
    page.locator("button[data-testid='stBaseButton-primary']").first.click(force=True, timeout=timeout)


# ── main ─────────────────────────────────────────────────────────────────
def run():
    from playwright.sync_api import sync_playwright

    BASE = "http://localhost:8501"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        # =========================================================
        # 1. WELCOME SCREEN
        # =========================================================
        page.goto(BASE, wait_until="networkidle")
        ss(page, "01_welcome_screen")

        # =========================================================
        # 2. Click Sign In
        # =========================================================
        click_btn(page, "Sign In")
        page.wait_for_timeout(2000)
        ss(page, "02_workspace_gateway")

        # =========================================================
        # 3. Click Employee Portal (first overlay)
        # =========================================================
        click_overlay(page, 0)
        page.wait_for_timeout(2000)
        ss(page, "03_demo_sandbox_employee")

        # =========================================================
        # 4. Click Karan Joshi (first profile)
        # =========================================================
        click_overlay(page, 0)
        page.wait_for_timeout(5000)
        ss(page, "04_employee_home")

        # =========================================================
        # 5. Click + New Request
        # =========================================================
        click_btn(page, "+ New Request")
        page.wait_for_timeout(3000)
        ss(page, "05_new_request_form")

        # Fill form for Self-Help (password reset)
        page.get_by_placeholder("e.g. Cannot connect to VPN").fill("Cannot reset password")
        page.get_by_placeholder(
            "What happened? Include error messages, when it started, and anything you already tried."
        ).fill("I am unable to reset my laptop password. I have tried the standard recovery but keep getting 'access denied' errors. Need help ASAP.")

        # Submit request
        click_btn(page, "Submit request")
        page.wait_for_timeout(25000)
        ss(page, "06_ticket_result_self_help")

        # =========================================================
        # 6. Create printer ticket (Team Assist / Hand 2)
        # =========================================================
        click_btn(page, "← Back to workspace")
        page.wait_for_timeout(2000)
        ss(page, "07_employee_home_with_tickets")

        click_btn(page, "+ New Request")
        page.wait_for_timeout(2000)

        page.get_by_placeholder("e.g. Cannot connect to VPN").fill("Printer not working on 3rd floor")
        page.locator('label').filter(has_text="high").click()
        page.get_by_placeholder(
            "What happened? Include error messages, when it started, and anything you already tried."
        ).fill("The HP LaserJet on the 3rd floor near conference room B is showing error 79 and won't print. It started this morning after the overnight update.")

        click_btn(page, "Submit request")
        page.wait_for_timeout(25000)
        ss(page, "08_ticket_result_team_assist")

        # =========================================================
        # 7. Create security ticket (Specialist / Hand 3)
        # =========================================================
        click_btn(page, "← Back to workspace")
        page.wait_for_timeout(2000)
        click_btn(page, "+ New Request")
        page.wait_for_timeout(2000)

        page.get_by_placeholder("e.g. Cannot connect to VPN").fill("Suspicious login activity detected")
        page.locator('label').filter(has_text="high").click()
        page.get_by_placeholder(
            "What happened? Include error messages, when it started, and anything you already tried."
        ).fill("Multiple failed login attempts from unknown IP address 203.0.113.42 targeting my admin account.")

        click_btn(page, "Submit request")
        page.wait_for_timeout(25000)
        ss(page, "09_ticket_result_specialist")

        # =========================================================
        # 8. Ticket detail page
        # =========================================================
        ss(page, "10_ticket_detail")

        # =========================================================
        # 9. Back to workspace → sign out → Agent
        # =========================================================
        click_btn(page, "← Back to workspace")
        page.wait_for_timeout(3000)
        ss(page, "11_employee_home_final")

        click_btn(page, "Sign out")
        page.wait_for_timeout(4000)

        # Sign In
        click_btn(page, "Sign In")
        page.wait_for_timeout(2000)

        # Agent Workspace (second overlay)
        click_overlay(page, 1)
        page.wait_for_timeout(2000)
        ss(page, "12_agent_demo_sandbox")

        # Alex Chen (first profile)
        click_overlay(page, 0)
        page.wait_for_timeout(5000)
        ss(page, "13_agent_dashboard")

        # =========================================================
        # 10. Agent Queue
        # =========================================================
        try:
            click_btn(page, "Team queue")
        except:
            pass
        page.wait_for_timeout(3000)
        ss(page, "14_agent_queue")

        # =========================================================
        # 11. Open a ticket
        # =========================================================
        try:
            click_btn(page, "Open")
            page.wait_for_timeout(4000)
            ss(page, "15_agent_ticket_detail")
        except:
            pass

        # =========================================================
        # 12. Admin Console
        # =========================================================
        click_btn(page, "Sign out")
        page.wait_for_timeout(4000)

        click_btn(page, "Sign In")
        page.wait_for_timeout(1500)

        click_overlay(page, 1)  # Agent Workspace
        page.wait_for_timeout(1500)
        ss(page, "16_admin_demo_sandbox")

        # Admin is last profile
        btns = page.locator("button[data-testid='stBaseButton-secondary']")
        btns.nth(btns.count() - 1).click(force=True, timeout=15000)
        page.wait_for_timeout(5000)
        ss(page, "17_admin_dashboard")

        # =========================================================
        # 13. Audit Log
        # =========================================================
        try:
            click_btn(page, "Audit log")
        except:
            pass
        page.wait_for_timeout(2000)
        ss(page, "18_admin_audit_log")

        # =========================================================
        # 14. Dark Mode
        # =========================================================
        click_btn(page, "Sign out")
        page.wait_for_timeout(3000)

        try:
            page.locator('label').filter(has_text="Dark Mode").click(timeout=5000)
            page.wait_for_timeout(1000)
            ss(page, "19_dark_mode_welcome")
        except:
            pass

        browser.close()


if __name__ == "__main__":
    run()
