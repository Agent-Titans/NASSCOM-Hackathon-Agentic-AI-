# Security — secrets and API keys

## API keys

- Store only in **`.env`** (gitignored). Never commit, never paste in issues/Slack/demo slides.
- If a key appears in **chat, email, or screenshots**, **revoke and create a new key** in [Google AI Studio](https://aistudio.google.com/apikey).
- Restrict keys by IP or app where Google allows; use separate keys per developer if possible.

## Sharing with teammates

1. Karan creates or rotates key.
2. Share via **private 1:1** (not group with mentors/jury).
3. Each teammate maintains their own `.env` locally.
4. Copilot/ChatGPT: **never** paste the key into AI prompts.

## Demo day

- Prefer one machine with `.env` if quota is tight.
- Keyword classifier fallback if Gemini returns 429.

## PII

- Guardrail runs before SQLite write, Chroma ingest, and Gemini.
- Audit logs: redacted snippets only.
