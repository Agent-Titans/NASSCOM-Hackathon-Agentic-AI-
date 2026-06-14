# Colleague setup — SAARTHI (Use Case 1)

**Goal:** Clone → bootstrap RAG → run app → verify with Judge50 assessment.  
**Time:** ~10 minutes first run (Gemini batch embed for 1006 corpus vectors).

---

## Quick start

```bash
git clone <repo-url>
cd "Final Round Hackathon"
bash scripts/setup_venv.sh
source .venv/bin/activate
cp .env.example .env          # add GOOGLE_API_KEY=
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

Open **http://localhost:8501** · Password: **`1234`**

---

## Verify before demo

```bash
source .venv/bin/activate
python scripts/ui_smoke_test.py              # all portals (19 checks)
python scripts/master_assessment.py          # cached Master50 grand report
python scripts/judge50_assessment.py         # cached Judge50 Nasscom report
# python scripts/master_assessment.py --live --fresh   # full independent 50-ticket run (~12 min)
```

Open **`test-reports/master_report.html`** — grand score, F1, LLM jury, per-agent timing, RAI/LLD audit.  
Open **`test-reports/judge50_report.html`** — Nasscom firm-specific jury score and gaps.  
Methodology write-up: **`docs/MASTER_ASSESSMENT_METHODOLOGY.md`**

---

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Employee | `pallavi@user` | 1234 |
| Agent (Application) | `subbu@employee` | 1234 |
| Agent (SecOps) | `narsimha@employee` | 1234 |
| Admin | `admin@employee` | 1234 |

---

## Three live demo tickets

| Submit as employee | Expected |
|--------------------|----------|
| Forgot password / cannot login | Hand 1 · Access Management |
| Printer paper jam | Hand 2 · Infrastructure |
| AWS secret on public GitHub | Hand 3 · SecOps |

**Misroute fix:** Application agent → **Route** → SecOps confirms department on Routing Specialists desk.

---

## Judge50 test suite

**50 tickets** across 5 firms (10 each): JPMorgan Tech, HSBC Tech, Microsoft, Nasscom, Wipro.

| File | Purpose |
|------|---------|
| `data/set_judge50_scenarios.json` | Scenario definitions |
| `docs/judge50_results.json` | Latest routing results |
| `test-reports/judge50_report.html` | Pre-Nasscom jury report |

---

## Code map

| Path | What it does |
|------|----------------|
| `docs/saarthi_overview.html` | Product overview (what / why / how) |
| `docs/CODE_WALKTHROUGH.md` | Start-to-end code routing map |
| `src/ui/app.py` | Streamlit entry |
| `src/services/ticket_service.py` | Five-step pipeline |
| `src/ui/agent_portal.py` | Agent workspace + Route |
| `scripts/judge50_assessment.py` | Full assessment + HTML report |

---

## Bootstrap

```bash
python scripts/bootstrap_rag_environment.py
```

Builds Chroma (~1006 docs) + SQLite syn-* corpus (1000 tickets). Expected after bootstrap:

- Chroma ≈ 1006
- SQLite syn-* = 1000

---

## Git push (when ready)

```bash
git status
git add -A
git commit -m "Judge50 assessment, portal polish, test cleanup"
git push origin final-round-hackathon
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: streamlit` | `source .venv/bin/activate` |
| `database is locked` | Stop Streamlit, re-run bootstrap |
| Chroma count 0 | `python scripts/ingest_synthetic_corpus.py` |
| UI smoke fails | `python scripts/ui_smoke_test.py` — read FAIL lines |

See also: `docs/DEMO_CHECKLIST.md` · `design/LLD.html`
