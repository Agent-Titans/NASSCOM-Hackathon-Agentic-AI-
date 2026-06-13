#!/usr/bin/env python3
"""Test ticket creation and email notification."""
import asyncio
import os
import re
from playwright.async_api import async_playwright

BASE = "http://localhost:8501"
EMAIL = "pallavi@user"
PASSWORD = "1234"

TICKET_SUBJECT = "Test: VPN Connection Fails After Update"
TICKET_DESCRIPTION = (
    "After the latest Windows update on June 10, 2026, my Cisco AnyConnect VPN "
    "client fails to establish a connection. The error message says 'VPN service "
    "unavailable'. I have tried restarting the service and rebooting my machine "
    "but the issue persists. Please assist."
)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="tmp/test_video",
            record_video_size={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        # 1. Navigate
        print("[1] Navigating to app...")
        await page.goto(BASE, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # 2. Click Sign In to open login form
        print("[2] Clicking Sign In button...")
        await page.locator('button:has-text("Sign In")').first.click()
        await page.wait_for_timeout(3000)

        # 3. Fill credentials and login
        print("[3] Logging in as", EMAIL)
        await page.locator('input[aria-label="Email Address"]').fill(EMAIL)
        await page.locator('input[aria-label="Password"]').fill(PASSWORD)
        await page.locator('button:has-text("Sign In")').last.click()
        await page.wait_for_timeout(5000)
        print("    Logged in successfully")

        # 4. Click "+ New Request" to open the form
        print("[4] Clicking '+ New Request'...")
        new_req_btn = page.locator('button:has-text("New Request"), a:has-text("New Request")').first
        if await new_req_btn.count() > 0:
            await new_req_btn.click()
            print("    Clicked '+ New Request'")
        else:
            # Try expander
            expander = page.locator('text="Submit a new operational incident"').first
            if await expander.count() > 0:
                await expander.click()
                print("    Clicked expander header")
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path="tmp/test_02_new_request.png")

        # 5. Inspect the form
        print("[5] Inspecting form elements...")
        # Get visible inputs
        inputs = await page.query_selector_all('input')
        for i, inp in enumerate(inputs):
            typ = await inp.get_attribute('type') or 'none'
            ph = await inp.get_attribute('placeholder') or 'none'
            aid = await inp.get_attribute('aria-label') or 'none'
            vis = await inp.is_visible()
            if vis:
                print(f"    Input {i}: type={typ}, placeholder={ph}, aria-label={aid}")
        
        # Get visible textareas
        textareas = await page.query_selector_all('textarea')
        for i, ta in enumerate(textareas):
            ph = await ta.get_attribute('placeholder') or 'none'
            aid = await ta.get_attribute('aria-label') or 'none'
            vis = await ta.is_visible()
            if vis:
                print(f"    Textarea {i}: placeholder={ph}, aria-label={aid}")
        
        # Get all visible labels
        labels = await page.query_selector_all('label')
        for i, lbl in enumerate(labels):
            text = (await lbl.inner_text()).strip()
            vis = await lbl.is_visible()
            if vis and text:
                print(f"    Label {i}: {text[:80]}")

        # 6. Fill the form
        print("[6] Filling ticket form...")
        
        # Find subject/title - try various selectors
        filled_subject = False
        for selector in [
            'input[aria-label*="itle" i]',
            'input[aria-label*="ubject" i]',
            'input[placeholder*="itle" i]',
            'input[placeholder*="ubject" i]',
            'input[placeholder*="What" i]',
        ]:
            el = page.locator(selector).first
            if await el.count() > 0 and await el.is_visible():
                await el.fill(TICKET_SUBJECT)
                filled_subject = True
                print(f"    Subject filled via: {selector}")
                break
        
        if not filled_subject:
            # Try finding first visible text input that isn't email
            vis_inputs = page.locator('input[type="text"]:visible')
            count = await vis_inputs.count()
            for i in range(count):
                inp = vis_inputs.nth(i)
                ph = await inp.get_attribute("placeholder") or ""
                if "email" not in ph.lower() and "password" not in ph.lower():
                    await inp.fill(TICKET_SUBJECT)
                    filled_subject = True
                    print(f"    Subject filled via text input #{i}")
                    break

        # Find description textarea
        filled_desc = False
        for selector in [
            'textarea[aria-label*="escription" i]',
            'textarea[placeholder*="escription" i]',
            'textarea[placeholder*="detail" i]',
            'textarea:visible',
        ]:
            el = page.locator(selector).first
            if await el.count() > 0 and await el.is_visible():
                await el.fill(TICKET_DESCRIPTION)
                filled_desc = True
                print(f"    Description filled via: {selector}")
                break

        # Select category (Radio buttons)
        print("[6b] Selecting category...")
        for cat in ["Hardware", "Software", "Network", "Security"]:
            cat_label = page.locator(f'label:has-text("{cat}")').first
            if await cat_label.count() > 0 and await cat_label.is_visible():
                await cat_label.click()
                print(f"    Selected category: {cat}")
                await page.wait_for_timeout(1500)
                break

        # Select subcategory
        for sub in ["VPN", "Connectivity", "Printer", "Email", "Access", "Windows"]:
            sub_label = page.locator(f'label:has-text("{sub}")').first
            if await sub_label.count() > 0 and await sub_label.is_visible():
                await sub_label.click()
                print(f"    Selected subcategory: {sub}")
                await page.wait_for_timeout(1500)
                break

        # Fill contact email if visible
        contact_input = page.locator('input[aria-label*="ontact" i], input[placeholder*="company" i]').first
        if await contact_input.count() > 0 and await contact_input.is_visible():
            await contact_input.fill("pallavi@company.com")
            print("    Contact email filled")

        # Select priority if visible
        for pri in ["Medium", "High", "Low"]:
            pri_label = page.locator(f'label:has-text("{pri}")').first
            if await pri_label.count() > 0 and await pri_label.is_visible():
                await pri_label.click()
                print(f"    Selected priority: {pri}")
                break

        await page.wait_for_timeout(2000)
        await page.screenshot(path="tmp/test_03_form_filled.png")
        print("    Screenshot: tmp/test_03_form_filled.png")

        # 7. Submit ticket
        print("[7] Submitting ticket...")
        submit_found = False
        for text_match in ["Submit request", "Submit", "Create", "Raise", "Save"]:
            btn = page.locator(f'button:has-text("{text_match}")').first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                print(f"    Clicked '{text_match}' button")
                submit_found = True
                break
        
        if not submit_found:
            print("    WARNING: No submit button found")

        # Wait for processing
        print("[8] Waiting for AI pipeline processing...")
        await page.wait_for_timeout(15000)
        await page.screenshot(path="tmp/test_04_after_submit.png")
        print("    Screenshot: tmp/test_04_after_submit.png")

        # 9. Check for success
        print("[9] Checking for success...")
        page_text = await page.locator('body').inner_text()
        
        # Look for ticket ID pattern
        ticket_ids = re.findall(r'(?:TICKET|TKT|ID|Ticket)[\s:#-]*(\d{3,})', page_text, re.IGNORECASE)
        if ticket_ids:
            print(f"    *** TICKET IDs found: {ticket_ids} ***")
        
        # Look for success/assignment indicators
        for keyword in ["success", "created", "submitted", "ticket", "confirmation", "assigned", "queued", "routed", "hand"]:
            if keyword.lower() in page_text.lower():
                idx = page_text.lower().find(keyword.lower())
                snippet = page_text[max(0, idx-60):idx+100]
                print(f"    Found '{keyword}': ...{snippet.strip()[:180]}...")

        # Print page state
        print(f"\n    Final page text:\n{page_text[:1500]}")

        await browser.close()
        print("\n[DONE] Test complete")

if __name__ == "__main__":
    os.makedirs("tmp", exist_ok=True)
    asyncio.run(main())
