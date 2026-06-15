# SAARTHI — Nasscom jury submission

**Branch:** `final-round-hackathon`  
**Setup guide:** [`NASSCOM_JUDGE_SETUP.md`](NASSCOM_JUDGE_SETUP.md)

## What ships

| Area | Path |
|------|------|
| Application | `src/` |
| RAG corpus | `data/synthetic/tickets_1000.json` (+ `.csv`) |
| **Jury demo scenarios (20)** | `data/set_demo20_scenarios.json` |
| Demo20 results | `docs/demo20_results.json` |
| Demo20 report (HTML) | `test-reports/demo20_report.html` |
| Demo20 report (MD) | `docs/DEMO20_SELF_EVALUATION.md` |
| Business documentation | `docs/SAARTHI_BUSINESS_DOCUMENTATION.html` · `.md` |
| Design / LLD | `design/LLD.html`, `docs/saarthi_overview.html` |
| Report index | `test-reports/index.html` |

## Primary validation

**Demo20** — 20 clear-title jury demo tickets (password, VPN, printer, security, apps, network, DB).

```bash
source .venv/bin/activate
python scripts/demo20_assessment.py --live --fresh --delay 2.0
```

Outputs: F1, LLM jury score, latency, responsible AI / security checklist, HTML + MD reports.

## Quick start

```bash
bash scripts/setup_venv.sh && source .venv/bin/activate
cp .env.example .env    # set GOOGLE_API_KEY
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

Before jury: `python scripts/ui_smoke_test.py` · `bash scripts/prepare_handoff.sh`

## Archived evaluation suites

Historical datasets and prior runs: `~/Desktop/SAARTHI-submission-archive/`  
(Jury100 bulk run deferred — API rate limits on 100-ticket back-to-back eval.)
