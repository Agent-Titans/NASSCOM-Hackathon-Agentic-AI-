# SAARTHI — IT ticket routing

**SAARTHI** · Five AI agents → Three Hands · Nasscom Agentic AI Hackathon 2026 (UC1)

**Jury setup:** [`docs/NASSCOM_JUDGE_SETUP.md`](docs/NASSCOM_JUDGE_SETUP.md)

## Folder map

```
├── design/              # LLD & architecture (source of truth)
├── docs/
│   ├── NASSCOM_JUDGE_SETUP.md   # ★ jury clone → bootstrap → demo
│   ├── SUBMISSION.md            # What ships in this repo
│   ├── DEMO_CHECKLIST.md        # Pre-jury walkthrough
│   ├── SAARTHI_BUSINESS_DOCUMENTATION.html  # Business jury pack
│   └── saarthi_overview.html    # Product overview
├── src/                 # Application code
├── scripts/             # bootstrap, demo20_assessment, ui_smoke, run_app
├── data/
│   ├── synthetic/tickets_1000.json      # RAG corpus (1000 resolved tickets)
│   ├── set_demo20_scenarios.json      # 20 jury demo tickets
│   ├── app.db           # gitignored — local tickets
│   └── chroma/          # gitignored — vector index
└── test-reports/        # demo20_report.html + index.html
```

## Quick start (judges)

```bash
git clone https://github.com/Agent-Titans/NASSCOM-Hackathon-Agentic-AI-.git
cd NASSCOM-Hackathon-Agentic-AI- && git checkout final-round-hackathon
bash scripts/setup_venv.sh && source .venv/bin/activate
cp .env.example .env          # set GOOGLE_API_KEY
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

Open **http://localhost:8501** · Password: **`1234`**

## Demo logins

| Portal | Email | Password |
|--------|-------|----------|
| Employee | `pallavi@user` | 1234 |
| Agent | `subbu@employee` | 1234 |
| SecOps | `narsimha@employee` | 1234 |
| Admin | `admin@employee` | 1234 |

## Try these tickets (employee portal)

1. **Forgot password** → Hand 1 · Access Management  
2. **Printer paper jam** → Hand 2 · Infrastructure  
3. **Security incident: AWS secret on GitHub** → Hand 3 · SecOps  

Full list: `data/set_demo20_scenarios.json`

## Validation reports

Open **`test-reports/index.html`** in a browser — Demo20 F1, LLM jury, latency, security.

```bash
python scripts/ui_smoke_test.py
bash scripts/prepare_handoff.sh
```

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/NASSCOM_JUDGE_SETUP.md` | Machine setup for judges |
| `docs/SAARTHI_BUSINESS_DOCUMENTATION.html` | Business + technical overview |
| `design/LLD.html` | Low-level design |
| `docs/SUBMISSION.md` | Submission layout |

**Not committed:** `.env`, `data/app.db`, `data/chroma/` — bootstrap locally per machine.
