# Copilot — IT ticket routing

1. Progress: `docs/BACKLOG.md` — current phase only.
2. Architecture: `design/LLD.html` (five agents, Three Hands, SQLite, Chroma, Streamlit).
3. Style: `standards/apple-design.md`, `standards/apple-ui.md`.
4. Pipeline: Guardrail → Classifier → Router → Resolver → Supervisor. LLM only in Classifier + Resolver.
5. Never commit `.env`.
