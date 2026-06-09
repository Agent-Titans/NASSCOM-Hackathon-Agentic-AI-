# Team guide (Copilot / no Cursor Pro)

1. Read [`BACKLOG.md`](BACKLOG.md) — only work on **current phase**.
2. Copy `.env.example` → `.env`; get API key from Karan **privately**.
3. Run `python scripts/check_gemini_models.py`.
4. VS Code Copilot: repo includes `.github/copilot-instructions.md`.

**Prompt prefix:**

```
Follow design/LLD.html. Task ID from docs/BACKLOG.md: [P?_?].
Pipeline: Guardrail → Classifier → Router → Resolver → Supervisor.
LLM only in Classifier and Resolver. standards/apple-design.md for copy/errors.
```

## Secrets

- Never commit `.env`. Rotate key if leaked. See `docs/SECURITY.md`.
