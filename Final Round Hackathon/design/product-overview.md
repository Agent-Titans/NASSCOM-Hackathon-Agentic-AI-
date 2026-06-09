# Artificial intelligence — IT ticket routing — Simplified design

One system. One ticket. One decision: **which Hand takes it from here.**

This note is the product-facing source of truth: calm language, no noise, and the **application architecture** we present—**Three Hands**, **five AI agents**, **retrieval + confidence**, **Use Case 1 alignment**. Detail that does not serve the story lives in the technical LLD.

---

## What we are building

We route and resolve IT tickets the moment they arrive—**fast when we are sure**, **assisted when we are partly sure**, **human when we are not.**

- Less waiting. Less rework. No false confidence.

---

## The Three Hands

**Hands** are the only outcomes that matter. Everything upstream exists to choose **one** of them.

### Hand 1 — Self-help (high trust)

When classification and retrieval align with strong confidence:

- The requester sees **clear, ordered steps** (grounded in knowledge and similar resolved tickets).
- They confirm **fixed** or ask to **move to the team**.

*Example:* access recovery—portal → forgot password → reset link.  
*Requester sees:* steps first, not a queue.

### Hand 2 — Routed assist (medium trust)

When the issue is understood well enough to route but not to close alone:

- The ticket **lands in the right department** with priority and SLA.
- The assignee gets **suggested steps** and **similar past tickets** so work starts in minutes, not hours.

### Hand 3 — Human first (low trust or policy)

When confidence is low, retrieval is weak, the issue is ambiguous, or policy says so (e.g. security-sensitive):

- The ticket goes to a **human queue** with an **escalation flag** and audit context.
- Automation steps aside. **Safety over speed.**

---

## How we decide (Supervisor AI agent)

**One pipeline. One composite score. One Hand.**

The orchestrator runs **Guardrail → Classifier → Router → Resolver** in that order; the **Supervisor AI agent** runs last, reads every prior output, and assigns the Hand.

1. **Guardrail AI agent** — safe text for storage, embeddings, and models.
2. **Classifier AI agent** — Use Case 1 taxonomy (see alignment table below).
3. **Router AI agent** — department, priority, SLA from classification + urgency.
4. **Resolver AI agent** — retrieve similar tickets and KB chunks, then prompt **Gemini** with grounded context.
5. **Supervisor AI agent** — fuse signals, compute **\(C_{\text{total}}\)**, assign Hand 1 / 2 / 3 using **policy thresholds** (tunable; LLD is canonical).

*Example default bands:* \(C_{\text{total}} \geq 0.80\) → Hand 1 · \(0.60\)–\(0.79\) → Hand 2 · \(< 0.60\) or policy → Hand 3.

**Composite confidence (illustrative):**

\[
C_{\text{total}} = (\text{Similarity} \times 0.6) + (\text{Sentiment} \times 0.2) + (\text{Historical success} \times 0.2)
\]

- **Similarity** — match between this ticket and retrieved chunks (e.g. ChromaDB + embeddings). **This is the RAG signal.**
- **Sentiment** — tone signal for risk (may start simple in early builds; weight stays in the framework).
- **Historical success** — how often this category resolved well recently (from stored feedback).

**Rule of thumb:** higher \(C_{\text{total}}\) → Hand 1; middle band → Hand 2; below floor or policy trigger → Hand 3.  
**\(C_{\text{total}}\)** is stored with the ticket; the product surfaces a human-readable confidence where it helps triage and explainability.

---

## The five AI agents (hero architecture)

Order is fixed. Responsibility is clear.

| Step | AI agent | Job |
|------|----------|-----|
| 1 | **Guardrail AI agent** | Redact PII and scrub secrets **before** storage and **before** any model or embedding call. |
| 2 | **Classifier AI agent** | Map the ticket to **category and subcategory** (Use Case 1 domains). |
| 3 | **Router AI agent** | Choose **department**, **priority**, and **SLA** from classification + urgency. |
| 4 | **Resolver AI agent** | **Retrieve then generate:** query the vector store (e.g. ChromaDB) → pass top‑\(k\) chunks to **Gemini** → produce **resolution steps** and citations to similar tickets / KB. |
| 5 | **Supervisor AI agent** | Fuse signals → compute **\(C_{\text{total}}\)** → assign **Hand 1 / 2 / 3** → set escalation flags → drive notifications and persistence. |

**Notifications** sit beside this chain: acknowledgment, self-help message, routing notice, resolution feedback—timed so the requester is never guessing. They are **not** a sixth reasoning AI agent; they **execute** what the Supervisor AI agent decides.

---

## Retrieval-augmented resolution (why ChromaDB + Gemini)

Use Case 1 expects **suggested resolution** grounded in reality—not generic prose.

- **ChromaDB** (or equivalent) holds **embeddings** of historical tickets and KB articles.
- **Resolver AI agent** always runs: **embed query → nearest neighbors → prompt Gemini with those chunks** → steps the assignee or requester can follow.
- If retrieval returns nothing useful, that **lowers effective similarity** and the **Supervisor AI agent** steers toward **Hand 2 or Hand 3**—by design.

---

## Alignment — Use Case 1 taxonomy

User-facing wording can stay friendly; **classification must map** to the official categories.

| Use Case 1 category | We map to |
|---------------------|-----------|
| Infrastructure | Infrastructure |
| Application | Software / Application |
| Security | Security |
| Database | Database |
| Storage | Storage |
| Network | Network |
| Access Management | Access management (account, identity, permissions) |

**Gap to avoid:** vague “IT” buckets. The Classifier outputs **one primary Use Case row** plus optional sub-label for routing nuance.

---

## Feedback loop (short)

After the requester sees steps or hears from the team:

- **Worked** / **Did not work** (and optional note).
- Outcomes are **stored** and feed **historical success** and retrieval metadata over time.

The system **learns from failure**, not only from success.

---

## Supporting layers (minimal — detail in LLD)

**Identity & access** — Requesters and staff sign in with role-based permissions; sessions and audit so every action has an actor. *(JWT, cookies, rate limits: specified in LLD—not repeated here.)*

**Persistence** — Single source of truth: tickets, classifications, routings, resolutions, feedback, audit. *(SQLite/SQLAlchemy in current plan; full schema in LLD.)*

**Interfaces** — Requester portal: my tickets, status, feedback. Assignee workspace: queue, **\(C_{\text{total}}\)**, similar tickets, audit.

---

## Demonstration data

- **Live tickets:** we create them through the normal product flow; they persist in SQLite for **My tickets** / **My queue**.
- **ChromaDB corpus:** we will ingest controlled **synthetic** rows aligned to our Hand stories; we will optionally add a **public, anonymized** IT-helpdesk-style import with documented provenance. We will not load production employee or customer data into demonstration environments.

---

## Responsible & ethical AI

- **Guardrail AI agent first** — no raw PII in model prompts or careless logs.
- **Grounded answers** — Resolver AI agent is **RAG-first**; we do not invent steps without context when retrieval is empty.
- **Graceful degradation** — weak retrieval or low score → **Hand 3** from the Supervisor AI agent, not a confident wrong answer.
- **Auditability** — each AI agent decision is traceable for review and compliance.

---

## Evaluation intent (Round 2 targets)

| Metric | How we measure (design) | Round 2 target |
|--------|-------------------------|----------------|
| Classification accuracy | Golden set of 15 tickets vs expected Use Case 1 domain | ≥ 85% |
| Routing correctness | Expected queue + priority vs Router output | ≥ 85% |
| Escalation appropriateness | Security / ambiguous → Hand 3; high-similarity repeats → not Hand 3 | 100% on policy cases |
| Resolution usefulness | Worked / Did not work + assignee outcome | ≥ 70% positive on Hand 1 demos |
| End-to-end latency | Submit → Hand visible; per-agent audit timestamps | < 15 s typical (demo env) |

The LLD defines audit fields and reporting hooks; Round 3 adds live dashboards and expanded golden sets.

---

## Scope — future features (out of core delivery)

- Deeper sentiment and adaptive thresholds from feedback.
- Trend detection and safe automation where policy allows.

Not part of the core story now.

---

## Design principles

- **Human-centered** — the right Hand, immediately.
- **Minimal** — Three Hands, five AI agents, one score; nothing extra on the main path.
- **Honest** — confidence visible; escalation is a feature.
- **Coherent** — this document names **Hands** for outcomes; technical diagrams and LLD carry DDL, email templates, and API contracts.

---

*This file is the simplified architecture narrative; the LLD carries diagrams, data model, and API contracts.*
