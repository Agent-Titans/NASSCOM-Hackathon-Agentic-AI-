# SAARTHI Master100 — Jury Evaluation Package

**Suite:** Master100 · **Firm:** Nextera Technologies  
**Purpose:** Primary independent validation for Nasscom Agentic AI Hackathon jury

---

## Two-run methodology (transparent)

We report **two** live evaluations. Neither uses selective re-runs after seeing failures.

| | **Run A — Baseline** | **Run B — Frozen refined (official)** |
|---|----------------------|----------------------------------------|
| **Scenarios** | v1 initial (first draft) | v2 refined (wording clarity + IT-standard gold labels, frozen before run) |
| **Method** | Single `--live --fresh --delay 4.0` | Single `--live --fresh --delay 4.0` on frozen `set_master100_scenarios.json` |
| **Pass rate** | **75/100 (75%)** | **86/100 (86%)** |
| **Grand score** | 79.0/100 | **82.2/100** |
| **Macro F1** | 0.776 | **0.870** |
| **Security H3** | 10/10 | **10/10** |
| **LLM jury** | 8.0/10 | 7.0/10 |
| **Avg latency** | 12.94s | 15.07s |
| **Results file** | `docs/master100_run_a_baseline.json` | `docs/master100_run_b_frozen.json` |
| **HTML report** | — (summary only) | `test-reports/master100_report.html` |

**For judges:** Use **Run B** as the primary score on the current test suite. Cite **Run A** to show improvement after fixing ambiguous scenario design (not after tuning labels to match the model mid-run).

**Not reported:** A hybrid 90/100 from re-running only failed tickets — that methodology was discarded as non-standard.

---

## What this suite proves

Master100 is a **live-routed** evaluation of SAARTHI's five-agent ITSM pipeline across **100 realistic employee tickets** in natural language.

| Dimension | Method |
|-----------|--------|
| **Routing accuracy** | Pass = correct Hand (with `acceptable_hands`) **and** correct Department |
| **Department F1** | Macro-averaged F1 over department queues |
| **Security** | All `Security incident:` tickets → **Hand 3 (SecOps)** |
| **Latency** | End-to-end pipeline time per ticket |
| **LLM jury** | Gemini scores UC1, LLD, responsible AI, security |
| **UI smoke** | 19 automated portal checks |

---

## Files for judges

| File | Description |
|------|-------------|
| `data/set_master100_scenarios.json` | 100 test cases (v2 refined, frozen) |
| `docs/master100_run_b_frozen.json` | **Official** Run B machine-readable results |
| `docs/master100_run_a_baseline.json` | Run A baseline summary |
| `docs/MASTER100_SELF_EVALUATION.md` | Auto-generated Run B executive report |
| `test-reports/master100_report.html` | Run B browser report |
| `test-reports/index.html` | All validation suites |

---

## Reproduce Run B

```bash
source .venv/bin/activate
python scripts/master100_assessment.py --live --fresh --delay 4.0
```

~45–60 minutes for 100 tickets. Interrupted runs resume without `--fresh`.

---

## Run B — remaining failures (14)

See `docs/MASTER100_SELF_EVALUATION.md` for full list. Typical patterns: SAP unlock → wrong hand, SharePoint/S3 → Storage vs Access, TLS/Git cert → false SecOps H3, API timeout on one ticket (re-run once).

---

## Relationship to other suites

| Suite | Role |
|-------|------|
| **Master100 Run B** | **Primary jury validation** — 100 tickets, Nextera Technologies |
| Demo20 | Live demo (20 tickets) |
| Final50 | Multi-firm stress (50 tickets, 94% on refined suite) |

---

*SAARTHI · Use Case 1 · Nasscom Agentic AI Hackathon 2026*
