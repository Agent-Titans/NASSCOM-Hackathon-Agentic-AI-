# SAARTHI — Code structure

**Team:** Sagar, Sree, Subbu, Karan, Shashi Pathi, Narsimha, Gajanan, Satya Sai · [`TEAM.md`](TEAM.md)

This document explains **how the repository is organized** and **how a ticket moves through the system**. For a line-by-line debug path, see [`CODE_WALKTHROUGH.md`](CODE_WALKTHROUGH.md).

---

## Repository layout

```
├── src/                    # Application source
│   ├── ui/                 # Streamlit portals (employee, agent, admin)
│   ├── services/           # TicketService orchestrator, RAG, notifications
│   ├── agents/             # Guardrail, Classifier, Router, Resolver, Supervisor
│   ├── stores/             # SQLite + Chroma data access
│   ├── config/             # Departments, settings, routing policy
│   ├── clients/            # Gemini API client
│   └── db/                 # SQLAlchemy models, session
├── scripts/                # Bootstrap, assessments, smoke tests
├── data/                   # Scenario JSON, synthetic RAG corpus (app.db gitignored)
├── config/                 # routing_rules.json (deterministic Hand/dept rules)
├── design/                 # LLD.html — architecture source of truth
├── docs/                   # Jury docs, results JSON, team info
└── test-reports/           # HTML evaluation reports
```

---

## Runtime architecture

**Not pure LLM routing.** Gemini classifies and resolves; **rules route.**

```
Employee submit (Streamlit)
        │
        ▼
┌───────────────┐
│  Guardrail    │  PII redaction, injection scan → halt on SECURITY_FAIL
└───────┬───────┘
        ▼
┌───────────────┐
│  Retrieval    │  Chroma ANN + keyword Jaccard (1,006 corpus vectors)
└───────┬───────┘
        ▼
┌───────────────┐
│  Classifier   │  keyword → Gemini → RAG hint
└───────┬───────┘
        ▼
┌───────────────┐
│  Router       │  config/routing_rules.json — O(1), no LLM
└───────┬───────┘
        ▼
┌───────────────┐
│  Resolver     │  RAG-grounded steps or generated playbook
└───────┬───────┘
        ▼
┌───────────────┐
│  Supervisor   │  Final hand, confidence band, low-grounding flag
└───────┬───────┘
        ▼
  Ticket + artifacts → employee / agent queue
```

---

## Key modules

| Module | Path | Responsibility |
|--------|------|----------------|
| **Entry** | `src/ui/app.py` | Login, role routing |
| **Orchestrator** | `src/services/ticket_service.py` | Runs full pipeline |
| **Guardrail** | `src/agents/guardrail.py` | PII redaction, security halt |
| **RAG** | `src/services/ticket_retrieval.py` | Vector + keyword search |
| **Classifier** | `src/agents/classifier.py` | Category + confidence |
| **Router** | `src/agents/router.py` | Hand 1/2/3 + department queue |
| **Resolver** | `src/agents/resolver.py` | Resolution steps |
| **Supervisor** | `src/agents/supervisor.py` | Policy enforcement |
| **Departments** | `src/config/departments.py` | Category → queue mapping |
| **Employee UI** | `src/ui/employee_portal.py` | Submit, H1 self-help |
| **Agent UI** | `src/ui/agent_portal.py` | Queues, assign, Route |
| **Admin UI** | `src/ui/admin_portal.py` | KPIs, audit log |

---

## Three Hands (UC1)

| Hand | Meaning | Employee experience |
|------|---------|---------------------|
| **H1** | Self-help | Guided steps; Worked / Did not work |
| **H2** | Specialist | Routed to department queue (Network, Application, …) |
| **H3** | SecOps | Security incidents — **no unsafe self-help**; human review |

Security tickets must start with **`Security incident:`** in the title for forced H3 escalation.

---

## Data layer

| Store | Location | Contents |
|-------|----------|----------|
| Live tickets | `data/app.db` (local) | User-submitted tickets |
| RAG corpus | `data/synthetic/tickets_1000.json` | 1,000 resolved historical tickets |
| Vectors | `data/chroma/` (local) | ~1,006 embeddings |
| Routing rules | `config/routing_rules.json` | Deterministic Hand/dept lookup |

Bootstrap: `python scripts/bootstrap_rag_environment.py`

---

## Assessment scripts

Shared metrics/helpers live in `scripts/master_assessment.py` (imported by suite runners).

| Script | Suite |
|--------|-------|
| `master100_assessment.py` | **Primary** — 100 Nextera tickets |
| `demo20_assessment.py` | Live demo — 20 clear-intent tickets |
| `final50_assessment.py` | Multi-firm — 50 tickets |
| `clear50_assessment.py` | Enterprise breadth — 50 tickets |
| `ui_smoke_test.py` | 19 portal checks |

---

## Responsible AI (code paths)

- **PII:** `src/agents/guardrail.py` — redact before RAG/Gemini
- **Injection:** guardrail regex + Gemini scan; pipeline stops on fail
- **H3 force:** classifier keyword + `supervisor_policy.py` — no self-help on Security category
- **Audit:** `src/stores/audit_store.py` — per-agent events and timings

---

*See [`CODE_WALKTHROUGH.md`](CODE_WALKTHROUGH.md) for submit → queue file-level trace.*
