# SAARTHI — IT ticket routing

**SAARTHI** · Five AI agents → Three Hands. Nascom final round hackathon.

Colleague setup: [`docs/COLLEAGUE_SETUP.md`](docs/COLLEAGUE_SETUP.md)

## Folder map

```
├── design/              # Submitted LLD & architecture (source of truth)
├── docs/
│   ├── COLLEAGUE_SETUP.md   # ★ clone → bootstrap → demo (share with team)
│   ├── DEMO_CHECKLIST.md    # Jury walkthrough
│   ├── PORTAL_UC1_ASSESSMENT.md
│   ├── test-reports/        # HTML routing test reports (open index.html)
│   └── JUDGE_SETUP.md       # Short pointer → COLLEAGUE_SETUP
├── src/                 # Application code
├── scripts/             # bootstrap, ingest, seed, run_app, master_assessment, judge50, ui_smoke
├── data/
│   ├── synthetic/       # tickets_1000.json + tickets_1000.csv (RAG corpus)
│   ├── app.db           # gitignored — local tickets
│   └── chroma/          # gitignored — vector index
└── test-reports/        # HTML assessment reports (open index.html)
```

## Quick start

**Python 3.10+** (`pyproject.toml`). On Mac:

```bash
brew install python@3.11
bash scripts/setup_venv.sh
source .venv/bin/activate
cp .env.example .env          # set GOOGLE_API_KEY
pip install -r requirements-ai.txt
python scripts/bootstrap_rag_environment.py   # SQLite + Chroma + 1k corpus
bash scripts/run_app.sh
```

**Stop Streamlit** before bootstrap if the app is already running.

Models: `gemini-2.5-flash` (classify/resolve) · Chroma uses **Gemini** `gemini-embedding-001` (default). Set `RAG_EMBEDDING_BACKEND=local` only for offline fallback.

## Demo logins

**Password:** `1234` for all accounts.

| Portal | Example emails |
|--------|----------------|
| Employee | `pallavi@user`, `gajanan@user`, `requester@demo.local` |
| Agent | `sree@employee` (Hardware), `narsimha@employee` (SecOps) |
| Admin | `admin@employee` |

Full list: `src/config/demo_auth.py`

## Try these subjects

- **Password reset** → Hand 1 Self-Help (guided steps)
- **Printer jam** → Hand 2 Team Assist (department queue)
- **Security breach** → Hand 3 Specialist (SecOps, no auto steps)

## RAG corpus

- **1,000 synthetic RESOLVED tickets** in `data/synthetic/tickets_1000.json` (+ **`tickets_1000.csv`** for Excel)
- **SQLite** — transactional + RESOLVED metadata
- **ChromaDB** — **Gemini** embedding vectors for retrieval (`RAG_EMBEDDING_BACKEND=gemini`)

Sample titles reference demo assignees (Sree, Subbu, Narsimha, etc.) for realistic RAG matches.

Re-ingest only:

```bash
python scripts/ingest_synthetic_corpus.py          # rebuild Chroma + SQLite syn-*
python scripts/ingest_synthetic_corpus.py --smoke  # + retrieval smoke test
python scripts/export_synthetic_corpus_csv.py      # refresh CSV from JSON
```

## New teammate

1. **`docs/COLLEAGUE_SETUP.md`** — environment + bootstrap (share this)
2. **`test-reports/index.html`** — routing accuracy reports
3. `design/LLD.html` — architecture source of truth

## Git sync

Active branch: `final-round-hackathon` — `git pull` before work, `git push` when done.

**Committed:** code, `data/synthetic/tickets_1000.json`, scripts  
**Not committed:** `data/app.db`, `data/chroma/`, `.env` — each machine runs `bootstrap_rag_environment.py` locally.

## Verify before demo

```bash
source .venv/bin/activate
python scripts/ui_smoke_test.py
python scripts/judge50_assessment.py
```

Open `test-reports/judge50_report.html` for the Nasscom pre-judge report.
