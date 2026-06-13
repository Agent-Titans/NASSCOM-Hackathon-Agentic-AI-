#!/usr/bin/env python3
"""Standalone SMTP smoke test — reads credentials from .env (never commit passwords)."""
from __future__ import annotations

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config.settings import get_settings  # noqa: E402

settings = get_settings()
smtp_user = settings.smtp_user or os.environ.get("SMTP_USER", "")
smtp_pass = settings.smtp_password or os.environ.get("SMTP_PASSWORD", "")
sender = settings.sender_email or smtp_user
recipient = os.environ.get("NOTIFICATION_RECIPIENT", smtp_user)

if not smtp_user or not smtp_pass:
    print("Set SMTP_USER and SMTP_PASSWORD in .env before running this test.")
    raise SystemExit(1)

html = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
<div style="background: #1a237e; color: white; padding: 20px; text-align: center;">
  <h1>SAARTHI - Ticket Notification</h1>
</div>
<div style="padding: 20px; background: #f5f5f5;">
  <h2>SMTP smoke test</h2>
  <p>If you received this, outbound email is configured correctly.</p>
</div>
</body>
</html>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = "SAARTHI SMTP smoke test"
msg["From"] = sender
msg["To"] = recipient
msg.attach(MIMEText(html, "html"))

try:
    server = smtplib.SMTP(settings.smtp_host or "smtp.gmail.com", settings.smtp_port or 587, timeout=15)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()
    print("SUCCESS - HTML email sent")
    print(f"From: {sender}")
    print(f"To: {recipient}")
except Exception as exc:
    print(f"ERROR: {type(exc).__name__}: {exc}")
    raise SystemExit(1) from exc
