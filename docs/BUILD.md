# How we build

**Order:** Phase 0 → 1 → 2 → 3 → 4 → 5. Track tasks in [`BACKLOG.md`](BACKLOG.md).

**Why Hand 3 UI before Hand 1?** After phase 2, demo security ticket (phase 4-7) before RAG-heavy Hand 1 (needs phase 3).

## Team split (3 people)

| Who | Phases | Folders |
|-----|--------|---------|
| **Pipeline** | 2, 3 | `src/agents/`, `src/services/`, `scripts/` |
| **UI** | 4 | `src/ui/`, `assets/` |
| **Quality** | 1, 5 | `tests/`, `docs/results.md` |

**Copilot users:** [`TEAM.md`](TEAM.md) + `.github/copilot-instructions.md`

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GOOGLE_API_KEY
python scripts/init_db.py
python scripts/seed_users.py
streamlit run src/ui/app.py
```

## LLD authority

`design/LLD.html` — five agents, Three Hands, SQLite, Chroma, Streamlit.
