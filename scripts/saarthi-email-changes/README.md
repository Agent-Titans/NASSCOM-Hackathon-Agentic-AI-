# SAARTHI Email Changes — June 11, 2026

## Files in this folder

| File | Description |
|------|-------------|
| `email_service.py` | Updated email service with template variable replacements |
| `new_ticket_notification.html` | Redesigned email template (inline CSS, matches login notification) |
| `login-email-notification.html` | Reference template (original design) |
| `email_preview.html` | Rendered preview of the ticket notification email |
| `test_send_email.py` | Standalone SMTP test script |
| `test_ticket_email.py` | Playwright test for ticket creation + email |
| `env-email-settings.txt` | Email-related `.env` settings |

## Changes made

### 1. `src/services/email_service.py`
- Added template variables: `ticket_id_short`, `ticket_hand`, `ticket_status_class`, `ticket_urgency`, `sender_email`
- Added `_status_css_class()` helper for status pill styling
- Proper `MIMEMultipart("alternative")` with `text/html` content type

### 2. `src/templates/new_ticket_notification.html`
- Full redesign to match `login-email-notification.html` layout
- All CSS inlined (no `<style>` tags) for Gmail compatibility
- Removed `color-mix()` — using plain RGBA colors instead
- Table-based lifecycle strip (no `display:flex`)
- Sections: Header → Info Card → Summary Table → Description → Lifecycle → CTA → Warning → Footer

### 3. `.env`
- Changed `SENDER_EMAIL` from `noreply@saarthi.com` to `nchary05@gmail.com`
- Gmail SMTP requires sender = authenticated user

### 4. Bug fix: `src/ui/employee_portal.py`
- Fixed `IndentationError` at line 571 (`try:` block over-indented)

## Known issue
- Emails sent to same address (`nchary05@gmail.com` → `nchary05@gmail.com`) go to Gmail Trash
- **Fix:** Change `NOTIFICATION_RECIPIENT` in `.env` to a different email address
