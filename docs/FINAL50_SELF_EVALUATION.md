# SAARTHI Final50 — Final Self-Evaluation Report

**Generated:** 2026-06-15T15:18:59.963860+00:00

## Executive summary

| Metric | Value |
|--------|-------|
| **Routing pass rate** | **47/50 (94%)** |
| **Grand score** | **91.1/100** |
| **Department macro-F1** | 0.924 |
| **Security H3 correct** | 5/5 |
| **Avg latency** | 13.95s (p50 16.96s, p90 25.25s) |
| **UI smoke** | PASS |

## LLM jury

- **Overall:** 9/10 (gemini)
- **Verdict:** SAARTHI ITSM demonstrates exceptional performance in ticket routing and classification, underpinned by a robust architecture and flawless handling of security-critical incidents, though latency presents a minor area for optimization.
- **Responsible AI:** 8
- **Ethical AI:** 8
- **Security posture:** 10

## Responsible AI / security checklist

- **LLD Pipeline Order:** 10.0/10 — Guardrail → Retrieval → Classifier → Router → Resolver → Supervisor (ticket_service.py)
- **Deterministic Routing:** 10.0/10 — RouterAgent uses cached routing_rules.json — O(1) hash lookup, no LLM
- **Security Guardrail:** 9.5/10 — PII redaction + injection regex + Gemini scan; pipeline halt on SECURITY_FAIL
- **Privacy / PII:** 9.5/10 — Email, phone, secrets redacted before retrieval and downstream LLM
- **Responsible AI:** 9.2/10 — low_grounding flags, Hand 3 human review, audit trail per agent step
- **Ethical AI:** 9.0/10 — No auto-assign without grace period; transparent hand/department on every ticket
- **RAG Grounding:** 9.0/10 — Chroma + keyword Jaccard + rag_gate trusted match before Hand 1
- **Scalability:** 8.8/10 — Chroma ANN O(log n), process caches, background index warm, SQLite → Postgres-ready ORM
- **Cost Efficiency:** 9.0/10 — Local ONNX embeddings (MiniLM), keyword short-circuit, resolver skips LLM on RAG hit
- **Open Source / Offline:** 8.5/10 — RAG_EMBEDDING_BACKEND=local, Chroma, keyword index — demo without embed API
- **API Integration Ready:** 9.0/10 — Gemini client swappable; settings-driven models; SMTP hooks for notifications
- **Dynamic Configuration:** 8.7/10 — routing_rules.json, supervisor_mode, rag_corpus_mode, department taxonomy via config
- **UC1 Use Case Alignment:** 9.3/10 — Three Hands, dept queues, employee + agent + admin portals, specialists desk

## Classify source mix

- **gemini:** 34
- **keyword:** 13
- **rag:** 3

## Gemini API usage

- **Tickets with Gemini:** 50/50
- **Model usage:** {'gemini-embedding-001': 50, 'gemini-2.5-flash': 45}

## Per-agent timing (avg ms)

- **classifier:** 4125ms
- **guardrail:** 3ms
- **resolution_format:** 3ms
- **resolver:** 10067ms
- **retrieval:** 669ms
- **router:** 3ms
- **supervisor:** 4ms

## Failures (3)

- AM08: expected Network / H2, got Access Management / H2
- TS01: expected Application / H2, got Infrastructure / H2
- TS02: expected Application / H2, got Infrastructure / H2