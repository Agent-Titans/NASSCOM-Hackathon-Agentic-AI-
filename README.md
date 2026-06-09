# ClearHand — IT ticket routing (Nascom final round)

**ClearHand** · Five AI agents → Three Hands. Build tracker: [`docs/BACKLOG.md`](docs/BACKLOG.md)

## Folder map

```
├── design/              # Submitted LLD & architecture (source of truth)
│   ├── LLD.html
│   ├── architecture.html
│   ├── product-overview.md
│   └── expectations.md
├── docs/
│   ├── BACKLOG.md       # ★ progress — update every task
│   ├── BUILD.md         # phases & team split
│   ├── TEAM.md          # Copilot teammates
│   └── SECURITY.md
├── standards/           # Apple HIG rules (not a new architecture)
│   ├── apple-design.md
│   └── apple-ui.md
├── src/                 # Application code
├── scripts/             # init_db, seed, ingest, check models
├── config/              # routing rules, settings
├── data/                # sqlite + chroma (gitignored)
└── tests/
```

## Quick start

**Python 3.10+ required** (`pyproject.toml`). On Mac: `brew install python@3.11` then:

```bash
brew install python@3.11      # once per machine (already done if setup succeeded)
bash scripts/setup_venv.sh    # creates .venv with Python 3.11
source .venv/bin/activate
cp .env.example .env          # GOOGLE_API_KEY from lead
pip install -r requirements-ai.txt
python scripts/init_db.py
python scripts/seed_users.py
pytest tests/ -q              # verify pipeline
bash scripts/run_app.sh       # or: streamlit run src/ui/app.py
```

**Demo logins:** `requester@demo.local` · `hardware@demo.local` · `secops@demo.local` · `admin@demo.local`

**Try these subjects:**
- Password reset → **Self-Help** (guided steps)
- Printer issue → **Team Assist** (Hardware queue)
- Security breach → **Specialist** (SecOps, no auto steps)

Models: `gemini-2.5-flash` + `gemini-embedding-001` — run `python scripts/check_gemini_models.py`

## New teammate

1. `docs/BACKLOG.md` — where we are  
2. `design/LLD.html` — what we build  
3. `docs/TEAM.md` — if using Copilot  

## Git sync

Active branch: `final-round-hackathon` — `git pull` before work, `git push` when done.
