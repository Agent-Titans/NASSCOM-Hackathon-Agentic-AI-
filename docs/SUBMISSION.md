# SAARTHI — Submission layout

Nasscom UC1 jury handoff. Primary self-evaluation: **Jury100** (100 live-routed tickets).

Archive of prior suites: `~/Desktop/SAARTHI-submission-archive/`

## What ships

| Area | Path |
|------|------|
| Application | `src/` |
| RAG corpus | `data/synthetic/tickets_1000.json` (+ `.csv`) |
| Evaluation scenarios | `data/set_jury100_scenarios.json` |
| Results | `docs/jury100_results.json` |
| Self-eval report (MD) | `docs/JURY100_SELF_EVALUATION.md` |
| Self-eval report (HTML) | `test-reports/jury100_report.html` |
| Design / LLD | `design/LLD.html`, `docs/saarthi_overview.html` |
| Business documentation | `docs/SAARTHI_BUSINESS_DOCUMENTATION.pdf` · `.html` · `.md` |

## Run Jury100 evaluation

```bash
source .venv/bin/activate
python scripts/jury100_assessment.py --live --fresh --delay 2.0
```

Generates F1, LLM jury score, per-firm breakdown, pass/fail table, and latency stats.

## Quick start (demo app)

```bash
bash scripts/setup_venv.sh && source .venv/bin/activate
cp .env.example .env
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

Before jury: `bash scripts/prepare_handoff.sh` · `python scripts/warm_cache.py`
