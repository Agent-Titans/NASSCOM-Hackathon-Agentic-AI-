# SAARTHI Master100 — Final Self-Evaluation Report

**Generated:** 2026-06-15T17:07:49.940159+00:00

## Executive summary

| Metric | Value |
|--------|-------|
| **Routing pass rate** | **86/100 (86%)** |
| **Grand score** | **82.2/100** |
| **Department macro-F1** | 0.87 |
| **Security H3 correct** | 10/10 |
| **Avg latency** | 15.07s (p50 15.7s, p90 28.23s) |
| **UI smoke** | PASS |

## LLM jury

- **Overall:** 7/10 (gemini)
- **Verdict:** SAARTHI ITSM shows promise with strong routing accuracy and good macro-F1, but requires improvement in classification accuracy and robustness against edge cases.
- **Responsible AI:** 7
- **Ethical AI:** 8
- **Security posture:** 9

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

- **gemini:** 59
- **keyword:** 40
- **rag:** 1

## Gemini API usage

- **Tickets with Gemini:** 100/100
- **Model usage:** {'gemini-embedding-001': 100, 'gemini-2.5-flash': 90, 'gemini-2.5-flash-lite': 2}

## Per-agent timing (avg ms)

- **classifier:** 3787ms
- **guardrail:** 3ms
- **resolution_format:** 3ms
- **resolver:** 11984ms
- **retrieval:** 646ms
- **router:** 4ms
- **supervisor:** 4ms

## Failures (14)

- NX008: expected Access Management / H2, got Application / H3
- NX013: expected Application / H1, got Infrastructure / H2
- NX014: expected Access Management / H2, got Storage / H2
- NX023: expected Application / H2, got Infrastructure / H2
- NX025: expected Application / H2, got Access Management / H2
- NX028: expected Application / H2, got Access Management / H2
- NX064: expected Application / H2, got Storage / H2
- NX068: expected Database / H2, got Storage / H3
- NX070: expected Storage / H2, got Application / H2
- NX072: expected Infrastructure / H2, got Application / H2
- NX074: expected Infrastructure / H2, got Application / H2
- NX094: expected Network / H2, got SecOps / H3
- NX095: expected Infrastructure / H2, got Application / H2
- NX096: expected Application / H2, got SecOps / H3