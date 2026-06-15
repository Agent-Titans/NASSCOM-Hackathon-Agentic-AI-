# SAARTHI Demo20 — Jury Demo Self-Evaluation

**Generated:** 2026-06-15T10:53:44.607775+00:00

## Executive summary

| Metric | Value |
|--------|-------|
| **Routing pass rate** | **16/20 (80%)** |
| **Grand score** | **82.1/100** |
| **Department macro-F1** | 0.781 |
| **Security H3 correct** | 3/3 |
| **Avg latency** | 11.46s (p50 13.64s, p90 29.14s) |
| **UI smoke** | PASS |

## LLM jury

- **Overall:** 8.5/10 (gemini)
- **Verdict:** SAARTHI ITSM presents a robust solution with excellent security and architectural adherence, demonstrating good performance, though its classification accuracy requires further refinement.
- **Responsible AI:** 7.5
- **Ethical AI:** 7.0
- **Security posture:** 9.5

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

- **gemini:** 13
- **keyword:** 7

## Per-agent timing (avg ms)

- **classifier:** 4966ms
- **guardrail:** 7ms
- **resolution_format:** 5ms
- **resolver:** 6947ms
- **retrieval:** 784ms
- **router:** 5ms
- **supervisor:** 5ms

## Failures (4)

- DM13: expected Infrastructure / H2, got Application / H2
- DM15: expected Application / H1, got Infrastructure / H2
- DM16: expected Network / H2, got SecOps / H3
- DM20: expected Database / H2, got Storage / H2