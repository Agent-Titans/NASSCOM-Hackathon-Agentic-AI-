# Apple design standards — how we build (does NOT replace the LLD)

> **This is not a new architecture.** Your submitted design is unchanged and remains authoritative:
> [`design/LLD.html`](../design/LLD.html) · [`design/architecture.html`](../design/architecture.html) · [`design/product-overview.md`](../design/product-overview.md)

**What this file is:** Apple **Human Interface** ideas (Clarity, Deference, Depth) applied as **quality rules** for copy, code layout, errors, audit, and Streamlit — so the *same* five agents, Three Hands, SQLite, Chroma, and Gemini RAG feel calm and honest. We did not add agents, change the pipeline order, or swap databases.

**UI details:** [`APPLE_UI_PRINCIPLES.md`](APPLE_UI_PRINCIPLES.md)

**North star:** *Clarity, Deference, Depth* — Apple HIG vocabulary, **LLD structure stays canonical.**

---

## 1. Clarity (understand in 10 seconds)

### Product & language

| Do | Don't |
|----|-------|
| **Hand 1 / 2 / 3** with plain subtitles | Internal codes (`PATH_A`, `c_total_band_2`) on requester screens |
| **Self-help**, **Routed assist**, **Specialist review** | “Resolver output”, “embedding score” to end users |
| One sentence per Hand on marketing/demo | Five agent names before outcome |

### Architecture (mirrors LLD — do not change without LLD update)

These bullets **restate** your LLD for design discipline; they are not a redesign:

- **One orchestrator:** `TicketService.process_ticket()` — per LLD.
- **Fixed pipeline order:** Guardrail → Classifier → Router → Resolver → Supervisor — per LLD Figure 6.
- **One score, one Hand:** Supervisor + `c_total` — per LLD; UI does not re-decide.

### Code & repo

```
src/
  agents/       # pure logic, no Streamlit imports
  services/     # orchestration, notifications
  stores/       # sqlite, chroma, audit
  models/       # pydantic + sqlalchemy
  ui/           # streamlit only
```

- File names match LLD: `guardrail.py`, `classifier.py`, not `agent1.py`.
- Public functions have docstrings that state **purpose** and **Hand impact**, not implementation trivia.

### APIs & contracts

- Pydantic models mirror LLD artifacts: `SanitizedText`, `ClassificationResult`, `RoutingResult`, `ResolutionResult`, `SupervisorDecision`.
- JSON from Gemini validated with schema; invalid → keyword fallback (Classifier) or `low_grounding` (Resolver).

### Errors (human-readable)

| Situation | User sees | Log/audit stores |
|-----------|-----------|------------------|
| Pipeline running | “We’re reviewing your request…” | per-agent `started` / `completed` |
| Hand 3 | “A specialist will review this.” | `escalation_required`, policy reason |
| Gemini down | “We couldn’t auto-suggest steps; your ticket is queued.” | `gemini_timeout` |
| Unsafe input | “Your ticket was sent for manual review.” | `guardrail_block` — no raw PII in log |

---

## 2. Deference (content and safety first)

### Data deference

- **SQLite** = truth; **Chroma** = memory for RAG only.
- **Guardrail before** embed, store, or LLM — no exceptions.
- Requester UI **defers** to Hand outcome: don’t show agent chain on home.

### LLM deference

- LLM only where judgment/generation is needed (Classifier, Resolver).
- Router and Supervisor stay **deterministic** — predictable, auditable, fair for Nascom comparison.
- RAG before generation: Chroma chunks in prompt; empty retrieval → lower Hand, not invented steps.

### Logging deference

- Audit: **what** happened and **which Hand**, not full prompts.
- Never log raw ticket text after guardrail; log `sanitized_hash` or redacted snippet max 80 chars.

### Notification deference

- Notifications **execute** Supervisor decision; they don’t re-classify or re-route.

---

## 3. Depth (progressive detail)

### Layers of detail

| Audience | Depth |
|----------|-------|
| Requester | Status → Hand label → steps or SLA or escalation |
| Assignee | Queue → ticket → suggestions + similar + SLA + confidence band |
| Admin | Audit timeline → export |
| Jury / dev | LLD, `MASTER_BACKLOG`, metrics, agent timings |

### Audit depth

- Append-only `AUDIT_LOG`: `event_type`, `agent`, `duration_ms`, `hand`, `policy_trigger` optional.
- Assignee **expander** “Why this Hand?” — summary derived from audit, not raw JSON dump.

### Documentation depth

- `README` → `MASTER_BACKLOG` → `IMPLEMENTATION_GUIDE` → LLD HTML.
- Same story at every level; deeper docs add schema and method names.

---

## Visual system (shared tokens)

Use across UI, HTML design docs, and slide decks:

| Token | Value | Use |
|-------|-------|-----|
| Background | `#f5f5f7` | App chrome |
| Surface | `#ffffff` | Cards |
| Text primary | `#1d1d1f` | Headings |
| Text muted | `#6e6e73` | Secondary |
| Accent | `#0071e3` | Primary actions, links |
| Success | `#34c759` | Hand 1, resolved |
| Warning | `#ff9500` | SLA soon |
| Critical | `#ff3b30` | Hand 3, breach |
| Radius | `12–16px` | Cards |
| Font stack | `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif` | Streamlit CSS |

---

## Agent design checklist (each agent)

- [ ] Single responsibility sentence in module header
- [ ] No UI imports in `src/agents/`
- [ ] Writes one artifact type to SQLite
- [ ] Emits one audit event (start + complete)
- [ ] Documented fallback path (LLD error handling)
- [ ] Unit test with golden input/output

---

## Three Hands system mapping

| Hand | System behavior | Primary modules |
|------|-----------------|-----------------|
| 1 | High `c_total`, strong grounding | Resolver, NotificationService, feedback |
| 2 | Medium band, routed queue | Router, Resolver (assist), assignee queue |
| 3 | Low band / policy / weak RAG | Supervisor policy, human queue, no fake steps |

---

## Nascom / fairness

- **Bucket A** = only behaviors described in submitted LLD.
- **Bucket C** = verbally “designed extension”, not shipped — keeps comparison fair.
- Apple principle here: **honesty** — don’t show features that aren’t in the build.

---

## Sign-off (system-wide)

- [ ] Naming consistent: Hands, agents, stores
- [ ] No PII in logs or vector index
- [ ] LLM map documented in README
- [ ] All Bucket A behaviors traceable to LLD section
- [ ] UI matches tokens in `APPLE_UI_PRINCIPLES.md`
