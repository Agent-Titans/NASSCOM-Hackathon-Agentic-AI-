# Build backlog

> **Update this file when you finish a task.** Change `[ ]` → `[x]` and refresh the counts at the top.  
> **Canonical architecture:** `design/LLD.html` (unchanged Nascom design)

---

## Where we are (read this first)

| | |
|---|---|
| **Current phase** | **3 — Chroma RAG** |
| **Doing now** | P3-1 GeminiClient embed + generate |
| **Progress** | **25 / 52** tasks |
| **Blocked?** | None |

**Phases:** `0 Foundation` → `1 Database` → `2 Agents` → `3 RAG` → `4 UI & Hands` → `5 Demo` → *(later B extras)*

| Phase | What | Done | Total | State |
|-------|------|------|-------|-------|
| **0** | Foundation | 5 | 5 | done |
| **1** | Database | 8 | 8 | done |
| **2** | Agent pipeline | 12 | 12 | done |
| **3** | Chroma RAG | 0 | 7 | **NOW** |
| **4** | UI + 3 Hands | 0 | 12 | |
| **5** | Metrics + jury | 0 | 8 | |
| B | Nice-to-have (after 5) | 0 | 6 | later |
| C | Slides only | — | 9 | never code |

---

## How to use (teammates)

1. Pick a task **only from the current phase** (or your assigned ID).
2. Mark `[ ]` → `[x]` when it **runs on your machine**.
3. Put your name in **Owner** if you want credit / coordination.
4. **Do not** build Bucket C features in the app.

**Status:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked (write why in Notes)

---

## Phase 0 — Foundation

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P0-1 | `requirements.txt` installs | | [x] | `pip install -r requirements.txt` |
| P0-2 | Folder layout `src/` `scripts/` `data/` `config/` | | [x] | Matches README tree |
| P0-3 | `config/settings.py` loads `.env` | | [x] | Prints config without key |
| P0-4 | `config/routing_rules.json` sample | | [x] | Router can load later |
| P0-5 | Streamlit `src/ui/app.py` boots | | [x] | `streamlit run src/ui/app.py` |

---

## Phase 1 — Database (SQLite)

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P1-1 | SQLAlchemy models: User, Ticket | | [x] | |
| P1-2 | Models: AuditLog, Feedback | | [x] | |
| P1-3 | Models: Classification, Routing, Resolution artifacts | | [x] | |
| P1-4 | `scripts/init_db.py` creates tables | | [x] | `data/app.db` exists |
| P1-5 | `scripts/seed_users.py` (requester, 2 assignees, admin) | | [x] | 4 users in DB |
| P1-6 | `TicketStore.create` / `update_status` | | [x] | Insert ticket row |
| P1-7 | `AuditLogStore.record` append-only | | [x] | Row after fake event |
| P1-8 | Ticket timestamps for metrics | | [x] | `created_at` set |

---

## Phase 2 — Agent pipeline (no pretty UI yet)

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P2-1 | Guardrail agent (PII, secrets) | | [x] | email → redacted |
| P2-2 | Classifier + Gemini JSON | | [x] | category returned |
| P2-3 | Classifier keyword fallback | | [x] | works if API off |
| P2-4 | Router rules → queue, priority, SLA | | [x] | security → SecOps |
| P2-5 | Resolver stub (no RAG yet) | | [x] | returns empty steps OK |
| P2-6 | Supervisor `c_total` + Hand 1/2/3 | | [x] | formula matches LLD |
| P2-7 | `TicketService.process_ticket` orchestrator | | [x] | one call runs all 5 |
| P2-8 | Audit row per agent + duration_ms | | [x] | 5+ events per ticket |
| P2-9 | Persist classification artifact | | [x] | DB row |
| P2-10 | Persist routing artifact | | [x] | on ticket row |
| P2-11 | Persist resolution artifact | | [x] | DB row |
| P2-12 | Policy: security → Hand 3 | | [x] | pytest e2e |

---

## Phase 3 — Chroma RAG

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P3-1 | `GeminiClient` embed + generate | | [ ] | `check_gemini_models.py` |
| P3-2 | Chroma persistent client | | [ ] | folder under `data/chroma` |
| P3-3 | `data/synthetic/` sample corpus | | [ ] | 3+ Hand demo stories |
| P3-4 | `scripts/ingest_corpus.py` | | [ ] | collection has chunks |
| P3-5 | Guardrail on ingest | | [ ] | no raw email in index |
| P3-6 | Resolver full RAG path | | [ ] | steps + citations |
| P3-7 | Empty retrieval → `low_grounding` | | [ ] | Supervisor → Hand 2/3 |

---

## Phase 4 — UI & three Hands

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P4-1 | Login / role in session | | [ ] | requester vs assignee |
| P4-2 | Requester: list my tickets | | [ ] | |
| P4-3 | Requester: new ticket form | | [ ] | triggers pipeline |
| P4-4 | Processing spinner (&lt;15s) | | [ ] | |
| P4-5 | Hand 1 detail (steps + feedback) | | [ ] | demo password ticket |
| P4-6 | Hand 2 detail (team + SLA) | | [ ] | demo printer ticket |
| P4-7 | Hand 3 detail (escalation only) | | [ ] | demo security ticket |
| P4-8 | Assignee queue by department | | [ ] | |
| P4-9 | Assignee detail (suggestions + similar) | | [ ] | |
| P4-10 | Apple theme CSS `assets/theme.css` | | [ ] | `standards/apple-ui.md` |
| P4-11 | Human confidence label (High/Med/Low) | | [ ] | not raw float on home |
| P4-12 | Admin audit page (read-only) | | [ ] | optional |

---

## Phase 5 — Demo & jury

| ID | Task | Owner | Status | Verify |
|----|------|-------|--------|--------|
| P5-1 | Golden set file `tests/golden/tickets.json` | | [ ] | ≥15 cases |
| P5-2 | pytest or script → `docs/results.md` | | [ ] | accuracy table |
| P5-3 | `docs/demo.md` script rehearsed | | [ ] | 3 Hands |
| P5-4 | Notification log after Hand | | [ ] | console OK |
| P5-5 | README quickstart works fresh clone | | [ ] | teammate test |
| P5-6 | No secrets in git | | [ ] | |
| P5-7 | LLM map in README | | [ ] | Classifier + Resolver only |
| P5-8 | Latency from audit timestamps | | [ ] | &lt;15s typical |

---

## Phase B — Later (after all Phase 5 `[x]`)

| ID | Task | Status |
|----|------|--------|
| B1 | SLA overdue badge | [ ] |
| B2 | Email notification stub | [ ] |
| B3 | Timeline on ticket detail | [ ] |
| B4 | Metrics dashboard page | [ ] |
| B5 | 30+ golden tickets | [ ] |
| B6 | Routing rules admin reload | [ ] |

---

## Phase C — Slides only (do not implement)

Teams, presence, phone escalation, Git tickets, K8s scale, shadow search, bulk admins, etc. — see old brainstorm; jury mention only.

---

## Notes / blockers

*(Write here)*

---

## Changelog

| Date | What |
|------|------|
| 2026-06-04 | Simplified repo + this backlog |
| 2026-06-04 | Phase 0 + 1 complete — app shell + SQLite |
| 2026-06-04 | Phase 2 complete — 5 agents + UI submit + pytest |
