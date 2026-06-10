# Master backlog — IT ticket routing (Nascom final round)

> **Single source of truth for build progress.** Update status on every merge or milestone.  
> New chat / new teammate: read this file first, then `tech/TECH_REQUIREMENTS.md`, then `IMPLEMENTATION_GUIDE.md`.

**Product:** Five AI agents → Three Hands → requester + assignee workspaces  
**Scope lock:** Features in **Bucket A** match submitted LLD. **Bucket B** only after A is demo-stable. **Bucket C** = jury narrative only (no app code unless explicitly promoted).

**Status legend**

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🟡 | In progress |
| ✅ | Done & verified in running app |
| ⏸️ | Blocked (note owner + blocker in *Notes*) |
| 🔵 | Presentation / roadmap only (Bucket C) |

**Last updated:** 2026-06-04 — Gemini models verified; Apple system design + Copilot guide added

**Design:** [`design/APPLE_SYSTEM_DESIGN.md`](design/APPLE_SYSTEM_DESIGN.md) (whole product) · [`design/APPLE_UI_PRINCIPLES.md`](design/APPLE_UI_PRINCIPLES.md) (Streamlit)  
**Teammates without Cursor:** [`COPILOT_TEAM_GUIDE.md`](COPILOT_TEAM_GUIDE.md)

---

## Quick health check (fill weekly)

| Area | Status | Owner | Notes |
|------|--------|-------|-------|
| Repo scaffold | ⬜ | | |
| SQLite schema + migrations | ⬜ | | |
| ChromaDB ingest + retrieval | ⬜
 | | |
| Gemini API wired | 🟡 | Karan | Models in `.env`; run `scripts/check_gemini_models.py` |
| 5-agent pipeline E2E | ⬜ | | |
| Hand 1 demo path | ⬜ | | |
| Hand 2 demo path | ⬜ | | |
| Hand 3 demo path | ⬜ | | |
| Golden-set metrics | ⬜ | | |
| Streamlit UI (Apple-style) | ⬜ | | |

---

## Bucket A — Must ship (LLD-aligned)

*Gate: **Bucket B** starts only when every **A** item marked ✅ has been smoke-tested on one machine.*

### A0 — Project foundation

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A0.1 | Python project layout (`src/`, `tests/`, `scripts/`, `data/`) | ⬜ | | `pip install -e .` or `requirements.txt` installs clean |
| A0.2 | `.env.example` + secrets not in git | ⬜ | | Gemini key only via env |
| A0.3 | `README` quickstart (clone → env → run → seed) | ⬜ | | Teammate can run in &lt;15 min |
| A0.4 | Config module (thresholds, `top_k`, SLA rules path) | ⬜ | | Change `c_total` bands without code hunt |

### A1 — Persistence (SQLite / SQLAlchemy)

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A1.1 | **USER** — `user_id`, `role`, `email` | ⬜ | | Seed requester + assignee + admin |
| A1.2 | **TICKET** — lifecycle fields, `hand`, `confidence`, `status` | ⬜ | | Create ticket persists |
| A1.3 | **CLASSIFICATION** artifact table / JSON column | ⬜ | | Written after Classifier |
| A1.4 | **ROUTING** — `department_queue`, `priority`, `sla_hours` | ⬜ | | Written after Router |
| A1.5 | **RESOLUTION** — steps, citations, `low_grounding` | ⬜ | | Written after Resolver |
| A1.6 | **AUDIT_LOG** — append-only, per-agent events | ⬜ | | Every agent step has row |
| A1.7 | **FEEDBACK** — worked / did not work + optional comment | ⬜ | | Updates after Hand 1 UI action |
| A1.8 | **VECTOR_METADATA** link ticket ↔ Chroma chunk ids | ⬜ | | Optional but in ERD |
| A1.9 | `TicketStore` + short transactions (`run_id` idempotency) | ⬜ | | No duplicate final status on retry |

**Sub-tasks — schema**

- ⬜ ERD matches LLD entities (USER, TICKET, AUDIT_LOG, FEEDBACK, VECTOR_METADATA)
- ⬜ State machine: Open → Redacting → Analyzing → Pending_Feedback / Human_Review → Resolved
- ⬜ Timestamps: `created_at`, routed, first response hooks for metrics

### A2 — Vector store (ChromaDB) + RAG corpus

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A2.1 | Chroma persistent client + collection naming | ⬜ | | Survives restart |
| A2.2 | Ingest script: synthetic CSV/JSON (Hand 1/2/3 stories) | ⬜ | | `scripts/ingest_corpus.py` completes |
| A2.3 | Guardrail on **ingest** (same rules as runtime) | ⬜ | | No raw PII in vectors |
| A2.4 | Chunking (~512-token blocks) + metadata (`category`, `source`) | ⬜ | | |
| A2.5 | Embeddings via Gemini embed API | ⬜ | | |
| A2.6 | `VectorStoreClient.query_similar(top_k=8, filters)` | ⬜ | | Returns chunks for demo tickets |
| A2.7 | Optional: public anonymized dataset import (document provenance) | ⬜ | | README cites source |

**Sub-tasks — RAG quality**

- ⬜ At least 3 corpus entries per Use Case 1 category used in golden set
- ⬜ Empty retrieval sets `low_grounding=true` in Resolver
- ⬜ Category filter on query when classification available

### A3 — External APIs & clients

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A3.1 | `GeminiClient` — classify JSON schema | ⬜ | | Valid JSON or fallback |
| A3.2 | `GeminiClient` — resolution generation w/ timeout + `max_tokens` | ⬜ | | |
| A3.3 | `GeminiClient` / pipeline — embeddings | ⬜ | | |
| A3.4 | Classifier keyword fallback (no second LLM) | ⬜ | | Force API fail → still category |
| A3.5 | Notification service (in-app + optional email stub) | ⬜ | | Async after Supervisor |

*API keys: see `tech/TECH_REQUIREMENTS.md` → **Credentials checklist**.*

### A4 — Five AI agents (fixed order)

| ID | Agent | LLM? | Status | Owner | Verification |
|----|-------|------|--------|-------|--------------|
| A4.1 | **Guardrail** — PII, secrets, injection hardening | No | ⬜ | | Unsafe input → Hand 3 or block |
| A4.2 | **Classifier** — Gemini JSON → Use Case 1 domain | Yes | ⬜ | | Maps to 7 official categories |
| A4.3 | **Router** — queue, priority, `sla_hours` | No | ⬜ | | Security → specialist policy |
| A4.4 | **Resolver** — embed → Chroma → Gemini RAG | Yes | ⬜ | | Steps + citations stored |
| A4.5 | **Supervisor** — `c_total` + policy → Hand 1/2/3 | No | ⬜ | | Bands 0.80 / 0.60 match LLD |

**Sub-tasks — orchestration**

- ⬜ `TicketService.process_ticket()` single entry point
- ⬜ Pipeline order enforced: G → C → R → Res → S (never skip)
- ⬜ Audit event per agent with duration_ms
- ⬜ Error paths: empty Chroma, Gemini timeout, bad JSON → safe Hand

**Sub-tasks — confidence formula**

- ⬜ `c_total = similarity*0.6 + sentiment*0.2 + historical_success*0.2`
- ⬜ `low_grounding` or policy → force Hand 3
- ⬜ Persist `c_total` + band on ticket

### A5 — Three Hands (product outcomes)

| ID | Hand | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A5.1 | **Hand 1** — self-help steps + feedback buttons | ⬜ | | Golden ticket e.g. password reset |
| A5.2 | **Hand 2** — dept queue + SLA + assignee suggestions | ⬜ | | Golden ticket e.g. printer/hardware |
| A5.3 | **Hand 3** — escalation, no fake steps, audit context | ⬜ | | Golden ticket e.g. security incident |
| A5.4 | Feedback loop updates historical_success signal | ⬜ | | Second ticket same pattern scores higher/lower appropriately |

### A6 — UI (Streamlit, Apple design — see design doc)

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A6.1 | Auth / role switch (requester, assignee, admin) | ⬜ | | RBAC: requester sees own tickets only |
| A6.2 | Requester: My tickets + New ticket + Ticket detail | ⬜ | | Hand-specific detail layouts |
| A6.3 | Assignee: My queue (priority, SLA remaining) | ⬜ | | Dept filter works |
| A6.4 | Assignee: Ticket detail — suggestions, similar cases, flags | ⬜ | | |
| A6.5 | Human-readable confidence line (not raw agent dump) | ⬜ | | |
| A6.6 | Processing state while pipeline runs (&lt;15s target) | ⬜ | | |
| A6.7 | Admin: read-only audit log view (minimal) | ⬜ | | Optional but LLD mentions |

**Sub-tasks — Apple HIG (implementation)**

- ⬜ Typography scale + generous whitespace (`docs/design/APPLE_UI_PRINCIPLES.md`)
- ⬜ Semantic colors (success / warning / critical for Hand outcome)
- ⬜ One primary action per screen
- ⬜ No internal agent math on requester home

### A7 — Security & responsible AI

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A7.1 | Guardrail before **any** embed or Gemini call | ⬜ | | Unit test with fake email in ticket |
| A7.2 | Prompt injection treated as data | ⬜ | | |
| A7.3 | Append-only audit for compliance story | ⬜ | | Export or UI view |
| A7.4 | Role-based access enforced in queries | ⬜ | | |

### A8 — Performance (LLD § Performance)

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A8.1 | Single retrieval pass per ticket | ⬜ | | |
| A8.2 | Embedding cache for near-duplicate sanitized text | ⬜ | | |
| A8.3 | `top_k` small (8) + bounded Gemini tokens | ⬜ | | |
| A8.4 | Async notifications after Hand decision | ⬜ | | |
| A8.5 | E2E latency measured (submit → Hand visible) | ⬜ | | Target &lt;15s demo env |

### A9 — Evaluation & demo package (Round 3 deliverables)

| ID | Item | Status | Owner | Verification |
|----|------|--------|-------|--------------|
| A9.1 | Golden set (≥15 tickets) with expected category + Hand | ⬜ | | CSV or pytest |
| A9.2 | Metrics: classification ≥85%, routing ≥85% | ⬜ | | Report in `docs/metrics/` |
| A9.3 | Escalation policy cases 100% | ⬜ | | Security / ambiguous → Hand 3 |
| A9.4 | Hand 1 usefulness ≥70% on demo set | ⬜ | | Feedback buttons |
| A9.5 | Three scripted demo paths (1/2/3) documented | ⬜ | | `docs/DEMO_SCRIPT.md` |
| A9.6 | Updated design doc matches built system | ⬜ | | |
| A9.7 | Git repo clean for jury clone | ⬜ | | No secrets committed |

### A10 — LLM usage inventory (jury question)

| Step | Uses Gemini? | Status | Documented in README? |
|------|--------------|--------|------------------------|
| Guardrail | No | ⬜ | |
| Classifier | Yes | ⬜ | |
| Router | No | ⬜ | |
| Resolver | Yes | ⬜ | |
| Supervisor | No | ⬜ | |
| Notifications | No | ⬜ | |

---

## Bucket B — After Bucket A is demo-stable

*Light implementation or UI-only; still defensible against LLD.*

| ID | Item | Status | Owner | Depends on | Verification |
|----|------|--------|-------|------------|--------------|
| B1 | SLA clock + “overdue” badge on assignee queue | ⬜ | | A1.4, A6.3 | Visual when past `sla_hours` |
| B2 | `sla_due_at` computed at route time | ⬜ | | A4.3 | Stored on ticket |
| B3 | SLA breach audit event (no auto-escalation tree) | ⬜ | | A1.6 | Log entry only |
| B4 | Timeline on ticket detail (created → routed → resolved) | ⬜ | | A1.6 | From audit timestamps |
| B5 | Admin config: routing rules YAML/JSON reload | ⬜ | | A0.4 | Admin role only |
| B6 | Email notification adapter (SMTP or log-to-console) | ⬜ | | A3.5 | Hand 2/3 notice |
| B7 | Expanded golden set (30+ tickets) | ⬜ | | A9.1 | |
| B8 | Simple metrics dashboard page (Streamlit) | ⬜ | | A9.2 | Classification confusion matrix |

---

## Bucket C — Jury / slides only (do not build unless promoted)

*Say: “Designed extension; omitted from demo to stay aligned with submitted LLD.”*

| ID | Topic | Status | Slide # | One-line pitch |
|----|-------|--------|---------|----------------|
| C1 | Microsoft Teams webhook notifications | 🔵 | | Same Hand decision, different channel |
| C2 | Assignee online/offline presence | 🔵 | | Teams/calendar integration |
| C3 | Phone/SMS if offline + SLA breach | 🔵 | | Escalation adapter |
| C4 | Accept-within-X-minutes workflow | 🔵 | | ACK timer on queue |
| C5 | Shadow/typeahead search over Chroma | 🔵 | | Preview before submit |
| C6 | Git / code-change ticket context | 🔵 | | PR/commit metadata in Resolver |
| C7 | Multi-region / Postgres / K8s scale story | 🔵 | | Architecture slide only |
| C8 | Adaptive thresholds from feedback ML | 🔵 | | LLD Future section |
| C9 | 10–15 admin bulk provisioning UI | 🔵 | | Seed users sufficient for demo |

**Promotion rule:** To move C → A or B, team lead updates this file + LLD addendum and agrees scope with Nascom fairness rule.

---

## Cross-cutting trackers

### Data sources (LLD requirement #8)

| Source | Used by | Ingest status | Runtime status |
|--------|---------|---------------|----------------|
| Synthetic ticket/KB CSV | Chroma + golden set | ⬜ | N/A |
| Live tickets (user-created) | SQLite | N/A | ⬜ |
| User feedback metadata | SQLite + historical_success | ⬜ | ⬜ |
| Live system logs (optional RCA) | Future / thin | ⬜ | ⬜ |

### Use Case 1 taxonomy coverage

| Category | Classifier maps | Corpus seeded | Golden ticket |
|----------|-----------------|---------------|---------------|
| Infrastructure | ⬜ | ⬜ | ⬜ |
| Application | ⬜ | ⬜ | ⬜ |
| Security | ⬜ | ⬜ | ⬜ |
| Database | ⬜ | ⬜ | ⬜ |
| Storage | ⬜ | ⬜ | ⬜ |
| Network | ⬜ | ⬜ | ⬜ |
| Access Management | ⬜ | ⬜ | ⬜ |

### Open decisions / missing inputs

| # | Question | Needed from | Blocking |
|---|----------|-------------|----------|
| 1 | ~~Gemini API key + model names~~ | Karan | **Done locally** — use `gemini-2.5-flash` + `gemini-embedding-001`; teammates get key privately |
| 2 | Subbu “comments” — ticket notes vs feedback? | Product | A1.7 copy |
| 3 | SMTP creds or console-only notifications for demo? | Team | B6 |
| 4 | Final repo host (GitHub org URL) | Team | A9.7 |
| 5 | Synthetic corpus file location / author | Data teammate | A2.2 |

---

## Changelog (milestones)

| Date | Milestone | Items closed |
|------|-----------|--------------|
| 2026-06-04 | Master backlog created | — |

---

## Related documents

| File | Purpose |
|------|---------|
| [`tech/TECH_REQUIREMENTS.md`](tech/TECH_REQUIREMENTS.md) | Stack, APIs, env vars, where each tech is used |
| [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) | Phases, team split, prompts for agents |
| [`design/APPLE_SYSTEM_DESIGN.md`](design/APPLE_SYSTEM_DESIGN.md) | Product + code + agents + audit |
| [`design/APPLE_UI_PRINCIPLES.md`](design/APPLE_UI_PRINCIPLES.md) | Streamlit UI layer |
| [`COPILOT_TEAM_GUIDE.md`](COPILOT_TEAM_GUIDE.md) | GitHub Copilot (free) workflow |
| [`SECURITY.md`](SECURITY.md) | API key handling |
| [`../low_level_design(LLD).html`](../low_level_design(LLD).html) | Canonical technical design |
| [`../Project_Structure_Simplified`](../Project_Structure_Simplified) | Product narrative |
