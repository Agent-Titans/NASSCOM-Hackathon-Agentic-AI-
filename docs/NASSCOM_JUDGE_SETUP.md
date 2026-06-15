# SAARTHI — Nasscom Jury Setup Guide

**Use Case 1** · Intelligent IT ticket routing · Agentic AI Hackathon 2026

**Goal:** Clone → configure API → bootstrap RAG → run live demo → open validation reports.  
**Time:** ~10–15 minutes on first machine (includes Gemini embedding index for 1,006 corpus vectors).

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.10+** | 3.11 recommended (`brew install python@3.11` on Mac) |
| **Git** | Clone from team repository |
| **Google AI Studio API key** | [aistudio.google.com](https://aistudio.google.com) → Create API key in a **new project** (fresh TPM quota) |
| **Network** | Required for Gemini classify, resolve, and embeddings |

---

## 2. Clone and install

```bash
git clone https://github.com/Agent-Titans/NASSCOM-Hackathon-Agentic-AI-.git
cd NASSCOM-Hackathon-Agentic-AI-
git checkout final-round-hackathon

bash scripts/setup_venv.sh
source .venv/bin/activate
pip install -r requirements-ai.txt
```

---

## 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL_CLASSIFY=gemini-2.5-flash
GEMINI_MODEL_RESOLVE=gemini-2.5-flash
GEMINI_MODEL_FALLBACKS=gemini-2.5-flash-lite
GEMINI_MODEL_EMBED=gemini-embedding-001
GEMINI_CLASSIFY_MAX_OUTPUT_TOKENS=512
RAG_EMBEDDING_BACKEND=gemini
RAG_AUTO_SEED=false
RAG_CORPUS_MODE=synthetic
```

Verify API access:

```bash
python scripts/check_gemini_models.py
```

---

## 4. Bootstrap RAG (one time per machine)

**Stop Streamlit** if running (avoids SQLite lock).

```bash
source .venv/bin/activate
python scripts/bootstrap_rag_environment.py
```

Expected after bootstrap:

- **0** live user tickets
- **1,000** RESOLVED `syn-*` tickets in SQLite
- **~1,006** vectors in ChromaDB (KB + synthetic corpus)

Optional warm-up before demo:

```bash
python scripts/warm_cache.py
```

---

## 5. Run the application

```bash
bash scripts/run_app.sh
```

Open **http://localhost:8501** · Password for all demo accounts: **`1234`**

---

## 6. Demo accounts

| Role | Email | What to show |
|------|-------|----------------|
| **Employee** | `pallavi@user` | Submit tickets, Hand 1 self-help steps |
| **Agent (Application)** | `subbu@employee` | Department queue, assign, resolve |
| **Agent (SecOps)** | `narsimha@employee` | Security queue, Routing Specialists |
| **Admin** | `admin@employee` | KPI dashboard, audit log, CSV export |

---

## 7. Recommended live demo tickets

Submit as **employee** (`pallavi@user`). Pipeline shows **stage-by-stage progress** (Guardrail → Retrieval → Classify → Route → Resolve → Supervisor).

| # | Title | Expected outcome |
|---|--------|------------------|
| 1 | Forgot password — cannot login to employee portal | Hand 1 · Access Management |
| 2 | Printer paper jam on 3rd floor | Hand 1/2 · Infrastructure |
| 3 | Security incident: AWS secret key found on public GitHub | Hand 3 · SecOps (no unsafe self-help) |

**Full jury demo suite (20 tickets):** `data/set_demo20_scenarios.json`  
**Misroute correction:** Agent → **Route** → SecOps Routing Specialists desk.

---

## 8. Validation reports (open in browser)

| Report | Path |
|--------|------|
| **Report index** | `test-reports/index.html` |
| **Master100 validation (primary)** | `test-reports/master100_report.html` |
| **Master100 jury package** | `docs/MASTER100_JUDGE_EVALUATION.md` |
| **Demo20 validation** | `test-reports/demo20_report.html` |
| **Business documentation** | `docs/SAARTHI_BUSINESS_DOCUMENTATION.html` |
| **Product overview** | `docs/saarthi_overview.html` |
| **Architecture (LLD)** | `design/LLD.html` |

Re-run Master100 live evaluation (optional — ~45–60 min, requires API quota):

```bash
python scripts/master100_assessment.py --live --fresh --delay 4.0
```

Re-run Demo20 live evaluation:

```bash
python scripts/demo20_assessment.py --live --fresh --delay 2.0
```

---

## 9. Pre-demo verification

```bash
source .venv/bin/activate
python scripts/ui_smoke_test.py       # 19 portal checks — must pass
bash scripts/prepare_handoff.sh       # clear live tickets, verify corpus
```

Walkthrough checklist: `docs/DEMO_CHECKLIST.md`

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | `source .venv/bin/activate` |
| `database is locked` | Stop Streamlit, re-run bootstrap |
| Gemini HTTP 429 / 503 | Wait 1–2 min; fallback uses `gemini-2.5-flash-lite`; use fresh API project |
| Chroma count 0 | `python scripts/ingest_synthetic_corpus.py` |
| UI smoke fails | Read FAIL lines from `python scripts/ui_smoke_test.py` |
| Slow first ticket (~15–25s) | Normal — two Gemini calls + RAG; security tickets &lt;2s |

---

## 11. Documentation map

| Document | Purpose |
|----------|---------|
| `docs/INDEX.md` | Documentation map |
| `docs/TEAM.md` | Builder names |
| `docs/CODE_STRUCTURE.md` | How the code is organized |
| `docs/MASTER100_JUDGE_EVALUATION.md` | Primary validation methodology |
| `docs/SAARTHI_BUSINESS_DOCUMENTATION.html` | Business + technical jury pack |
| `docs/SUBMISSION.md` | What ships in this repository |
| `docs/CODE_WALKTHROUGH.md` | Code routing map |
| `docs/DEMO_CHECKLIST.md` | Step-by-step jury walkthrough |
| `docs/SECURITY.md` | PII, guardrails, responsible AI |

---

*SAARTHI Team · Nasscom Agentic AI Hackathon 2026 · UC1*
