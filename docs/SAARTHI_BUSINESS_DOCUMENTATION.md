# SAARTHI — Intelligent IT Service Management
## Business & Technical Overview · Nasscom Agentic AI Hackathon 2026

**Document version:** 1.0 · June 2026  
**Use case:** UC1 — Classify, route, and resolve IT incidents with agentic AI  
**Classification:** Internal / Jury presentation

---

## Executive summary

**SAARTHI** (Sanskrit: *companion, guide*) is an agentic IT service management platform that automates the **first mile** of enterprise incident handling: every ticket is sanitized, classified, matched against historical resolutions, routed to the correct department and **Hand** (self-help, team assist, or specialist), and given actionable guidance — typically in **under 20 seconds**.

| Dimension | SAARTHI approach |
|-----------|------------------|
| **Problem** | Manual triage is slow, inconsistent, and expensive at scale |
| **Solution** | Five-agent AI pipeline + RAG + deterministic routing |
| **Outcome** | Faster resolution, reduced SLA risk, audit-ready decisions |
| **Validation** | Up to **88%** routing pass on 100-ticket live suites; macro-F1 up to **0.86** |
| **Responsible AI** | PII guardrails, security force-escalation, human-in-the-loop triage |

> **Development note:** This product was built with **AI-assisted engineering** (Cursor / LLM pair-programming) under human review, architecture governance, and structured test validation.

---

## 1. The problem we solve

Enterprise IT operations centres receive thousands of heterogeneous incidents daily:

- Password resets and access requests  
- Application outages (SAP, Teams, custom APIs)  
- Network and VPN failures  
- Database performance and backup issues  
- **Security incidents** requiring immediate specialist handling  

**Pain points:**

| Challenge | Business impact |
|-----------|-----------------|
| Manual triage & mis-routing | Wrong queue → hours of delay, SLA breach |
| Inconsistent categorisation | Poor reporting, repeated escalations |
| Tacit knowledge in senior agents | Long onboarding, tribal runbooks |
| Security under-triage | Compliance and breach risk |
| High cost per ticket | L1/L2 labour on repetitive work |

**SAARTHI** addresses the **classification → routing → initial resolution** gap so human agents focus on judgement, not inbox sorting.

---

## 2. Our solution — what SAARTHI does

SAARTHI ingests a natural-language ticket (title + description) and executes a **fixed, auditable pipeline**:

```
Employee / API submit
    → Guardrail (PII redaction, injection defence)
    → Retrieval (ChromaDB + 1,000 resolved tickets)
    → Classifier (Google Gemini 2.5 Flash)
    → Router (deterministic rules — no LLM)
    → Resolver (RAG-grounded or Gemini-generated steps)
    → Supervisor (confidence band + final Hand)
    → Employee portal / Agent queue / SecOps desk
```

**Deliverables per ticket:**

1. **Department queue** (Infrastructure, Application, Network, Database, Access Management, SecOps)  
2. **Hand** (1 = Self-Help, 2 = Team Assist, 3 = Specialist)  
3. **Resolution steps** (grounded when RAG match is strong)  
4. **Confidence score** and audit trail  
5. Optional **email notification** (SMTP integration)

---

## 3. Where we differentiate

| Capability | SAARTHI | Typical rule-only ITSM | Chatbot-only |
|------------|---------|------------------------|--------------|
| Semantic classification | Gemini + RAG context | Keyword rules | Generic LLM, no routing |
| Grounded resolution | 1k resolved ticket corpus | Static KB articles | Hallucination risk |
| Security policy | Force Hand 3 / SecOps | Manual escalation | Often under-triages |
| Explainability | Full agent audit log | Limited | Black box |
| Human override | Routing Specialists desk | Reassign only | No structured triage |
| Graceful degradation | Keyword + generic fallback on API limits | N/A | Fails or hallucinates |

**Key differentiators:**

- **RAG-first resolution** — steps from *similar resolved tickets*, not invented prose  
- **Deterministic router** — O(1) rule lookup; no LLM roulette on department  
- **Three Hands model** — aligns automation depth to confidence and policy  
- **Multi-portal UX** — Employee, Agent, Admin, SecOps Routing Specialists  
- **Enterprise scenario validation** — Microsoft, HSBC Tech, JPMorgan Tech, Capgemini patterns  

---

## 4. Architecture — five AI agents

| Agent | Role | Technology |
|-------|------|------------|
| **Guardrail** | PII redaction, prompt-injection scan | Regex + Gemini security scan |
| **Retrieval** | Find similar resolved tickets | ChromaDB ANN + keyword + Gemini embeddings |
| **Classifier** | Category & confidence hint | Gemini 2.5 Flash (primary) |
| **Router** | Hand + department queue | `routing_rules.json` (deterministic) |
| **Resolver** | Resolution steps & citations | RAG match or Gemini generate |
| **Supervisor** | Final Hand + confidence band | Weighted `c_total` formula (O(1)) |

**Design principle:** Only classify and resolve use generative AI; routing and supervision are **fast, repeatable, and testable**.

---

## 5. Three Hands & human-in-the-loop

### Hand 1 — Self-Help (high confidence)

Employee receives guided steps on the portal. Marks **Worked** or **Did not work** to close or escalate. Reduces L1 volume for password, printer, and known playbook issues.

### Hand 2 — Team Assist (medium confidence)

Ticket lands in the correct **department queue**. Agents assign, collaborate, resolve. Suggested steps and RAG references accelerate mean-time-to-resolution.

### Hand 3 — Specialist (security / low confidence)

Confirmed security incidents route to **SecOps** with **no unsafe self-help steps**. Human specialist required by policy.

### Human-in-the-loop — Routing Specialists

Agents can **escalate misroutes** to the SecOps Routing Specialists desk with a reason. Specialists perform **one-hop department correction** without re-running the full pipeline — preserving audit continuity while fixing edge cases.

**Triage model:** AI handles volume; humans handle ambiguity, policy exceptions, and security judgement.

---

## 6. RAG, Gemini embeddings & fallbacks

### Retrieval-Augmented Generation (RAG)

- **Corpus:** 1,000 resolved synthetic enterprise tickets (`tickets_1000.json` + CSV)  
- **Vector store:** ChromaDB with **local MiniLM** embeddings (default) or **Gemini `gemini-embedding-001`** (optional)  
- **Similarity gate:** Weak matches do not inflate confidence — `low_grounding` flag when appropriate  
- **Cache warming:** Background index + disk embedding cache on login (`warm_cache.py`)

### Gemini embedding usage

- **Query embedding** for semantic rescoring of top candidates (up to 16 per ticket)  
- **Corpus embeddings** cached on disk to avoid repeated API calls  
- **Batch embed** support for bootstrap / ingest  

### Graceful fallback chain (resilience)

| Stage | Primary | Fallback |
|-------|---------|----------|
| Classify | Gemini JSON | RAG neighbour → keyword index |
| Security prefix | `"Security incident:"` short-circuit | — |
| Resolve | RAG similar ticket | Gemini steps → hardware heuristics → generic steps |
| Embed | Gemini API | Skip semantic layer; Chroma local vectors + keywords |
| Guardrail scan | Gemini | Regex layer (fail-open on API error with logging) |
| HTTP 429/503 | Retry (2× backoff) | Degrade to keyword / cached paths |

**Live demo behaviour:** One ticket at a time (~15–20s) — well within API limits. Bulk evaluation scripts use delays and cache warm to respect rate limits.

---

## 7. Security, PII & responsible AI

| Control | Implementation |
|---------|----------------|
| **PII redaction** | Guardrail runs **before** SQLite, Chroma, and Gemini |
| **Prompt injection** | Regex patterns + Gemini untrusted-data scan |
| **Security incidents** | Force Hand 3; SecOps queue; no dangerous self-help |
| **Audit trail** | Append-only log: agent start/end, durations, RAG hit/miss |
| **API keys** | `.env` only — never committed |
| **Low grounding** | UI signals when steps are suggestions, not proven matches |
| **Human escalation** | Employee "Did not work" → Hand 2; agent Route → Specialists |

**Ethical stance:** Automate triage, not accountability. Security and compliance paths always retain human ownership.

---

## 8. Performance & validation

### Latency (live pipeline, end-to-end)

| Profile | Avg latency | Notes |
|---------|-------------|-------|
| Gemini-primary classify | **14–16 s** | Typical employee submit → routed ticket |
| Keyword-assisted path | **11–13 s** | When short-circuit applies |
| Security short-circuit | **&lt; 2 s** | `"Security incident:"` prefix |
| Resolver (Gemini) | **~8–10 s** | Largest single-agent cost |

Per-agent timing captured in SQLite audit (`guardrail`, `retrieval`, `classifier`, `router`, `resolver`, `supervisor`).

### Routing accuracy (validated live suites)

| Evaluation suite | Tickets | Pass rate | Macro F1 | Context |
|------------------|--------:|----------:|---------:|---------|
| Classifier fix — Judge100A | 100 | **88%** | **0.86** | Post Gemini-primary fix |
| Classifier opt — Judge100B | 100 | **86%** | **0.74** | Industrial / healthcare mix |
| Portal batch 50 | 50 | **82%** | **0.85** | Enterprise firms |
| Smoke30 | 30 | **90%** | — | Regression smoke |
| Jury100 (in progress) | 100 | Target ≥85% | — | Microsoft, HSBC Tech, JPMorgan Tech, Capgemini |

**Pass criteria:** Correct Hand (or acceptable alternatives) **and** correct department queue.

### SLA impact (business framing)

| Metric | Without SAARTHI | With SAARTHI |
|--------|-----------------|--------------|
| Time to first route | Minutes–hours (manual) | **~15–20 seconds** |
| Mis-route rate | Industry 15–30% | **12–15%** on validated suites |
| L1 deflection (Hand 1) | Low | Password / playbook tickets self-served |
| Audit readiness | Ad-hoc | Structured per-ticket agent log |

*SLA figures are illustrative based on triage automation; customer environments vary.*

---

## 9. Product features & portals

### Employee portal
- Create incidents with priority  
- View routing outcome, confidence, resolution steps  
- Hand 1 feedback: Worked / Did not work  

### Agent workspace
- Department-scoped queue (Infrastructure, Application, Network, etc.)  
- Assign, release, resolve  
- Route misroutes to Specialists  
- Filters: Unassigned, Mine, SLA at risk  

### Admin console
- KPI dashboard (open, resolved, queue depth)  
- All tickets + CSV export  
- Audit log with confidence % and RAG evidence  

### SecOps Routing Specialists
- Misroute review and one-hop correction  
- Security queue isolation  

### Additional capabilities
- **Reference articles** from similar resolved tickets  
- **Automation suggestions** on resolved patterns  
- **Email notifications** (SMTP — optional)  
- **Auto-assign** after configurable grace window  
- **UI smoke suite** — 19 automated portal checks  

---

## 10. Integrations, APIs & cloud hosting

| Layer | Current (hackathon) | Production path |
|-------|---------------------|-----------------|
| **LLM** | Google Gemini 2.5 Flash (classify, resolve) | Same + model routing / caching |
| **Embeddings** | Gemini embedding-001 or local MiniLM | Tenant-configurable |
| **UI** | Streamlit (Python) | React / Streamlit Cloud / containerised |
| **Database** | SQLite (ORM-ready) | PostgreSQL / Cloud SQL |
| **Vector DB** | ChromaDB (local persist) | Managed vector (Vertex, Pinecone) |
| **Auth** | Demo email/password | SSO / Entra ID / Okta |
| **Notifications** | SMTP (optional) | ServiceNow, Teams, PagerDuty webhooks |
| **Hosting** | Local / laptop demo | **GCP Cloud Run**, Azure App Service, or AWS ECS |
| **ITSM integration** | Standalone demo | ServiceNow / Jira SM REST ingest |

**API-ready design:** `TicketService.process_ticket()` is the single orchestration entry — wrap as REST for enterprise integration.

---

## 11. Team

| Area | Contributors |
|------|--------------|
| **Front end** | Sagar, Sree |
| **Back end** | Subbu, Sree, Karan, Shashi Pathi |
| **Testing & QA** | Narsimha, Gajanan |
| **UI / UX design** | Satya Sai, Subbu |
| **Documentation** | Shashi |

**Nasscom Agentic AI Hackathon 2026** · Use Case 1 — Intelligent IT ticket routing

---

## 12. AI-assisted development disclosure

SAARTHI was developed using **AI-assisted coding tools** (including Cursor IDE and large language models) for:

- Boilerplate, test harnesses, and scenario generation  
- Classifier prompt iteration and reconciliation logic  
- HTML assessment reports and documentation drafts  

All architecture decisions, security policies, routing rules, and validation results were **reviewed and owned by the human team**. Automated test suites (100-ticket live routing) provide evidence of production intent beyond prototype demos.

---

## 13. Demo quick reference

| Role | Email | Password |
|------|-------|----------|
| Employee | pallavi@user | 1234 |
| Agent (Application) | subbu@employee | 1234 |
| Agent (SecOps) | narsimha@employee | 1234 |
| Admin | admin@employee | 1234 |

**Three live demo tickets:**

1. *Forgot password* → Hand 1 · Access Management  
2. *Printer paper jam* → Hand 1/2 · Infrastructure  
3. *AWS secret on public GitHub* → Hand 3 · SecOps  

**Setup:** `docs/NASSCOM_JUDGE_SETUP.md` · **Reports:** `test-reports/index.html`

---

## 14. Future roadmap (Round 3 / production)

| Initiative | Benefit |
|------------|---------|
| **Parallel retrieval + classify** | Lower wall-clock latency without changing LLD agent boundaries |
| **Merged classify/resolve draft** | Single Gemini call for simple tickets when RAG is weak |
| **Duplicate-ticket fast cache** | String/fingerprint match bypasses full pipeline for repeat intents |
| **True token streaming UI** | `streamGenerateContent` + progressive step rendering |
| **Background notify/webhooks** | Non-blocking SMTP, ServiceNow, Teams integrations |

**Demo20 validation:** `data/set_demo20_scenarios.json` · `test-reports/demo20_report.html`

---

*© 2026 SAARTHI Team · Nasscom Agentic AI Hackathon · Confidential*
