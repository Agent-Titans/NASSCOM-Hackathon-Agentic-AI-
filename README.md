# SAARTHI — Intelligent IT Ticket Routing

**Nasscom Agentic AI Hackathon 2026** · Use Case 1  
**Team:** Sagar, Sree, Subbu, Karan, Shashi Pathi, Narsimha, Gajanan, Satya Sai — [`docs/TEAM.md`](docs/TEAM.md)

Five AI agents route every ticket to **Hand 1 self-help**, **Hand 2 specialist**, or **Hand 3 SecOps** — with RAG grounding and deterministic routing rules (not pure LLM routing).

---

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

Full guide: [`docs/NASSCOM_JUDGE_SETUP.md`](docs/NASSCOM_JUDGE_SETUP.md)

---

## Validation (live-routed)

| Suite | Result | Report |
|-------|--------|--------|
| **Master100** (primary) | **86/100** · F1 0.87 · security 10/10 | [`test-reports/master100_report.html`](test-reports/master100_report.html) |
| Final50 | 94% (47/50) | [`test-reports/final50_report.html`](test-reports/final50_report.html) |
| Demo20 | 80% (16/20) | [`test-reports/demo20_report.html`](test-reports/demo20_report.html) |

**Report hub:** [`test-reports/index.html`](test-reports/index.html)

---

## Demo (4 minutes)

| Portal | Email | Password |
|--------|-------|----------|
| Employee | `pallavi@user` | 1234 |
| Agent | `subbu@employee` | 1234 |
| SecOps | `narsimha@employee` | 1234 |
| Admin | `admin@employee` | 1234 |

Walkthrough: [`docs/DEMO_CHECKLIST.md`](docs/DEMO_CHECKLIST.md)

---

## Repository map

```
├── src/                 # Application (ui, agents, services, stores)
├── scripts/             # Bootstrap, assessments, smoke tests
├── data/                # Scenario JSON, synthetic RAG corpus
├── config/              # routing_rules.json
├── design/              # LLD.html (architecture)
├── docs/                # Team, judge setup, code structure, results
└── test-reports/        # HTML evaluation reports
```

**How the code works:** [`docs/CODE_STRUCTURE.md`](docs/CODE_STRUCTURE.md) · [`docs/CODE_WALKTHROUGH.md`](docs/CODE_WALKTHROUGH.md)

**All documentation:** [`docs/INDEX.md`](docs/INDEX.md)

---

## Pre-submission checks

```bash
python scripts/ui_smoke_test.py       # 19 portal checks
bash scripts/prepare_handoff.sh       # clean live tickets
python scripts/check_gemini_models.py # API health
```

**Not committed:** `.env`, `data/app.db`, `data/chroma/` — bootstrap per machine.

---

*SAARTHI Team · Agent-Titans · UC1 Intelligent Ticket Routing*
