# SAARTHI — Nasscom jury submission

**Team:** Sagar, Sree, Subbu, Karan, Shashi Pathi, Narsimha, Gajanan, Satya Sai — [`TEAM.md`](TEAM.md)  
**Branch:** `final-round-hackathon`  
**Setup:** [`NASSCOM_JUDGE_SETUP.md`](NASSCOM_JUDGE_SETUP.md) · **Doc index:** [`INDEX.md`](INDEX.md)

---

## What ships

| Area | Path |
|------|------|
| Application | `src/` |
| RAG corpus | `data/synthetic/tickets_1000.json` |
| **Primary scenarios (100)** | `data/set_master100_scenarios.json` |
| Demo scenarios (20) | `data/set_demo20_scenarios.json` |
| Master100 results | `docs/master100_run_b_frozen.json` |
| Master100 report | `test-reports/master100_report.html` |
| Judge evaluation pack | `docs/MASTER100_JUDGE_EVALUATION.md` |
| Business documentation | `docs/SAARTHI_BUSINESS_DOCUMENTATION.html` |
| Code structure | `docs/CODE_STRUCTURE.md` |
| Design / LLD | `design/LLD.html` |
| Report index | `test-reports/index.html` |

---

## Primary validation — Master100

100 human-style tickets for **Nextera Technologies**. Two-run methodology (transparent):

| Run | Pass rate | Notes |
|-----|-----------|-------|
| **Run A baseline** | 75/100 | First draft scenarios, blind |
| **Run B frozen (official)** | **86/100** | Refined scenarios, single full run |

```bash
python scripts/master100_assessment.py --live --fresh --delay 4.0
```

---

## Supporting validation

| Suite | Command | Role |
|-------|---------|------|
| Demo20 | `python scripts/demo20_assessment.py --live --fresh --delay 2.0` | Live 4-min demo tickets |
| Final50 | `python scripts/final50_assessment.py --live --fresh --delay 3.5` | Multi-firm stress |
| Clear50 | `python scripts/clear50_assessment.py --live --fresh` | Enterprise breadth |

---

## Quick start

```bash
bash scripts/setup_venv.sh && source .venv/bin/activate
cp .env.example .env    # set GOOGLE_API_KEY
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

Before jury: `python scripts/ui_smoke_test.py` · `bash scripts/prepare_handoff.sh`

---

## Archived (not for jury)

`docs/archive/` · `scripts/archive/` · `data/archive/` — superseded Jury100 / Master50 tooling.
