# SAARTHI — Code walkthrough (start to finish)

**Team:** Sagar, Sree, Subbu, Karan, Shashi Pathi, Narsimha, Gajanan, Satya Sai — [`TEAM.md`](TEAM.md)

This document traces a ticket from browser submit to agent queue. For repo layout see [`CODE_STRUCTURE.md`](CODE_STRUCTURE.md).

---

## 1. Application entry

| Step | File | What happens |
|------|------|----------------|
| Start app | `scripts/run_app.sh` → `src/ui/app.py` | Streamlit loads, `init_db()`, login page |
| Login | `src/ui/login_render.py` | Email + password checked against `User` table |
| Role routing | `src/ui/app.py` | `requester` → employee portal; `assignee` → agent; `admin` → admin console |

**Session keys:** `signed_in`, `user`, `page`, `portal_view`, `agent_view`, `ticket_id`

---

## 2. Employee submits a ticket

| Step | File | What happens |
|------|------|----------------|
| Create form | `src/ui/employee_portal.py` → `render_portal_create()` | Title, description, urgency |
| Persist row | `src/stores/ticket_store.py` → `TicketStore.create()` | New `Ticket` row, status `NEW` |
| Run pipeline | `src/services/ticket_service.py` → `process_ticket()` | Five-step processing (below) |
| Show result | `src/ui/employee_portal.py` | Redirect to detail or home with flash message |

---

## 3. Five-step processing pipeline

Orchestrated in `src/services/ticket_service.py` → `TicketService.process_ticket()`.

```
Employee submit
      │
      ▼
┌─────────────┐
│  Guardrail  │  src/agents/guardrail.py
└──────┬──────┘  PII redaction + injection scan. Security halt → Hand 3, stop.
       │
       ▼
┌─────────────┐
│  Retrieval  │  src/services/ticket_retrieval.py
└──────┬──────┘  Chroma vector search + keyword Jaccard fallback
       │
       ▼
┌─────────────┐
│ Classifier  │  src/agents/classifier.py
└──────┬──────┘  Category + confidence (keyword → API → RAG hint)
       │
       ▼
┌─────────────┐
│   Router    │  src/agents/router.py
└──────┬──────┘  Hand 1 / 2 / 3 + department queue
       │
       ▼
┌─────────────┐
│  Resolver   │  src/agents/resolver.py
└──────┬──────┘  Steps from RAG match or generated playbook
       │
       ▼
┌─────────────┐
│ Supervisor  │  src/agents/supervisor.py
└──────┬──────┘  Final hand, confidence band, low-grounding flag
       │
       ▼
 Ticket updated + artifacts saved
```

### 3.1 Guardrail

- **File:** `src/agents/guardrail.py`
- Redacts email, phone, secrets before any embedding or classify call.
- Regex layer blocks obvious prompt-injection phrases.
- On `SecurityGuardrailException`: ticket forced to Hand 3 / SecOps, pipeline stops.

### 3.2 Retrieval (RAG)

- **File:** `src/services/ticket_retrieval.py`
- **Index:** `src/stores/chroma_store.py` (vectors built by `scripts/ingest_synthetic_corpus.py`)
- **Corpus:** `data/synthetic/tickets_1000.json` (1000 resolved historical tickets)
- **Gate:** `src/services/rag_gate.py` — only trusts matches above similarity threshold
- **Cache:** `_CORPUS_STEMS` dict avoids re-tokenizing corpus on every search

### 3.3 Classifier

- **File:** `src/agents/classifier.py`
- **Prompt rules:** `src/agents/classifier_prompt.py`
- **API client:** `src/clients/gemini_client.py`
- **Keyword fallback:** `src/agents/keyword_index.py`
- Output: `use_case_category`, `confidence`, subcategory

### 3.4 Router

- **File:** `src/agents/router.py`
- Maps category → department via `src/config/departments.py` → `CATEGORY_TO_DEPARTMENT`
- Assigns **Hand:**
  - **Hand 1** — self-help (employee sees steps on portal)
  - **Hand 2** — department queue (agent assign / resolve)
  - **Hand 3** — SecOps / security specialist

### 3.5 Resolver

- **File:** `src/agents/resolver.py`
- If RAG match is trusted: reuse/adapt steps from similar resolved ticket
- Else: generate step list from category playbook
- **Format split:** `src/services/resolution_formatter.py` (requester vs assignee steps)

### 3.6 Supervisor

- **File:** `src/agents/supervisor.py`
- **Policy:** `src/config/supervisor_policy.py`
- May downgrade Hand 3 → 2 when confidence low; sets `low_grounding` flag
- **Automation hint:** `src/services/automation_suggestion.py` (repeat-pattern note on high similarity)

### 3.7 Persistence

| Store | File | Saves |
|-------|------|-------|
| Ticket | `src/stores/ticket_store.py` | hand, department_queue, status, assignee |
| Classification | `src/stores/artifact_store.py` | category, confidence JSON |
| Resolution | `src/stores/artifact_store.py` | steps JSON, references |
| Audit | `src/stores/audit_store.py` | pipeline events, RAG hit/miss, timings |
| Agent run | `src/stores/agent_run_store.py` | per-step guardrail_ok flag |

---

## 4. Department queues

**File:** `src/config/departments.py`

| Classifier category | Queue name |
|--------------------|------------|
| Infrastructure | Infrastructure |
| Application | Application |
| Network | Network |
| Security | SecOps |
| Database | Database |
| Storage | Storage |
| Access Management | Access Management |

Legacy names (`Hardware`, `Software`, `DBA`) map to canonical queues via `canonical_department()`.

---

## 5. Employee portal after routing

**File:** `src/ui/employee_portal.py`

| Hand | Employee sees |
|------|----------------|
| 1 | Resolution steps in expander; **Worked** / **Did not work** buttons |
| 2 | Routed message; assignee name when claimed |
| 3 | SecOps routing banner |

**Escalation:** "Did not work" → `TicketService` re-runs pipeline with Hand 2 escalation path.

---

## 6. Agent workspace

**File:** `src/ui/agent_portal.py`

| Action | Service / store |
|--------|-----------------|
| Queue list | `TicketStore` filtered by `user.department` |
| Assign to me | Sets `assignee_id`, status `IN_PROGRESS` |
| Release | Clears assignee, back to queue |
| Resolve | Status `RESOLVED` |
| Route (misroute) | `src/services/specialists_desk_service.py` → `request_specialist_review()` |

### Routing Specialists desk (SecOps)

**File:** `src/services/specialists_desk_service.py`

1. Agent clicks **Route** → ticket moves to `Specialists` queue, audit event logged.
2. SecOps opens ticket → sees **Routing context** expander (original dept, reason).
3. SecOps picks target department + **Route** → one-hop reroute to operational queue.
4. `OPERATIONAL_DEPARTMENT_SET` validates target in O(1).

---

## 7. Admin console

**File:** `src/ui/admin_portal.py`

- KPI dashboard from `src/services/admin_stats_service.py`
- All tickets table + CSV export
- Audit log with confidence %, RAG match id, agent timings

---

## 8. Notifications (optional)

**File:** `src/services/notification_service.py` + `src/services/email_service.py`

Disabled by default (`EMAIL_NOTIFICATIONS_ENABLED=false`). Hooks on open, assign, resolve, close.

---

## 9. Bootstrap on a new machine

```bash
python scripts/bootstrap_rag_environment.py
```

| Script step | Effect |
|-------------|--------|
| `clean_for_ui_demo.py` | Clears live tickets |
| `patch_rag_assignee_titles.py` | Names in corpus titles |
| `ingest_synthetic_corpus.py` | Chroma + SQLite syn-* rows |
| `export_synthetic_corpus_csv.py` | Excel-friendly CSV |

---

## 10. Test commands

```bash
python scripts/ui_smoke_test.py
python scripts/master100_assessment.py --live --fresh --delay 4.0
python scripts/demo20_assessment.py --live --fresh --delay 2.0
```

Reports: `test-reports/index.html`, `test-reports/master100_report.html`

---

## Quick file index

```
src/ui/app.py                    Entry + role routing
src/ui/employee_portal.py        Requester UI
src/ui/agent_portal.py           Assignee UI + Route actions
src/ui/admin_portal.py           Admin dashboard
src/services/ticket_service.py   Pipeline orchestrator
src/agents/*.py                  Guardrail, Classifier, Router, Resolver, Supervisor
src/services/ticket_retrieval.py RAG search
src/services/specialists_desk_service.py  Misroute correction
src/config/departments.py        Category → queue map
src/stores/ticket_store.py       Ticket CRUD + SLA labels
data/synthetic/tickets_1000.json RAG corpus
scripts/bootstrap_rag_environment.py  First-run setup
scripts/master100_assessment.py  Primary 100-ticket jury eval
scripts/demo20_assessment.py     Live demo eval
docs/CODE_STRUCTURE.md           Repo layout + architecture summary
docs/MASTER100_JUDGE_EVALUATION.md  Jury validation methodology
```
