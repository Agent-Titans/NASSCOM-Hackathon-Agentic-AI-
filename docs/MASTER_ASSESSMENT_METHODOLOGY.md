# SAARTHI Master Assessment — Methodology & Efficiency

Generated after Master50 validation (2026-06-14).

## Verdict

**POSITIVE — demo ready** · Grand score **94.2/100** · Routing **100%**

## What we tested

| Suite | Tickets | Purpose |
|-------|---------|---------|
| Master50 | 50 | Independent firms (Amazon, Google, Deloitte, Pfizer, Boeing, Nike, Tesla, Accenture, Reliance Jio, ICICI) — zero overlap with Judge50 |
| UI smoke | 19 | Employee, agent, admin portals |
| Architecture audit | 13 dimensions | LLD, privacy, security, scalability |
| LLM jury | 1 holistic + F1 | Optional Gemini judge on aggregate results |

## Routing metrics

- **Pass criteria:** correct Hand (or acceptable_hands) AND correct department queue
- **Macro-F1** on department labels across all 50 cases
- **Per-agent `duration_ms`** from SQLite audit log (`agent_completed` events)

## Latency & CPU reduction methodologies

### 1. Keyword-before-Gemini short-circuit
- Local inverted-index classifier runs **before** Gemini when score gap is decisive (`classifier_keyword_short_circuit=true`).
- Master50: **46** keyword classify + **4** RAG classify — **0 Gemini classify calls** on 50 tickets (resolver still uses Gemini only on RAG miss).
- Saves ~2–4 s API latency and API cost per short-circuited ticket.

### 2. Local ONNX embeddings (open-source path)
- `RAG_EMBEDDING_BACKEND=local` uses Chroma **all-MiniLM-L6-v2** (ONNX) — no embed API, works offline.
- Vector search is O(log n) approximate nearest neighbour on persisted Chroma index.

### 3. Tiered retrieval caches
- `process_cache.py`: retrieval candidate cache (128 entries), historical success cache, embedding cache on disk.
- `_CORPUS_STEMS`: stemmed tokens built once per process — O(1) per doc after warm-up.
- `retrieval_bootstrap.py`: background Chroma warm on login — non-blocking submit path.

### 4. Deterministic O(1) agents
- **Router:** `routing_rules.json` + `@lru_cache` — no LLM.
- **Supervisor:** weighted `c_total` formula — O(1) arithmetic.
- **Guardrail Layer 1:** regex injection scan before any API call.

### 5. Conditional LLM resolver
- Resolver copies RAG-matched steps when `trusted_similar` — **skips `generate_resolution`** (largest latency win on hits).
- Security category short-circuits resolver entirely.
- `resolution_rewrite_enabled=false` avoids a third LLM call.

### 6. Complexity summary

| Step | Time complexity | Notes |
|------|-----------------|-------|
| Guardrail regex | O(n) text | n = ticket length |
| Keyword classify | O(t·d) | t tokens, d small |
| Chroma query | O(log N) | N = corpus size |
| Corpus Jaccard | O(k) | k capped candidates |
| Router | O(1) | dict lookup |
| Supervisor | O(1) | fixed formula |

## Per-agent average timing (Master50)

| Agent | Avg duration |
|-------|--------------|
| guardrail | 4 ms |
| retrieval | 2216 ms |
| classifier | 1587 ms |
| router | 3 ms |
| resolver | 8711 ms |
| supervisor | 4 ms |
| resolution_format | 2 ms |

**Average end-to-end:** 11.38 s per ticket.

## Cost model

| Component | Default | Cost |
|-----------|---------|------|
| Chroma embed | Local MiniLM | Free / CPU only |
| Chroma embed | Gemini embed API | Per 1k tokens |
| Classify | Gemini 2.5 Flash | Per call; reduced by keyword short-circuit |
| Resolve | Gemini 2.5 Flash | Only on RAG miss |
| Router / Supervisor | Local | Free |

## Future scalability & dynamism

- **Database:** SQLAlchemy ORM — swap SQLite DSN for Postgres/MySQL without code changes.
- **Models:** `settings.py` model names — plug open-source classify via new client class.
- **Routing rules:** hot-reload `routing_rules.json` + `supervisor_mode` without redeploy.
- **Corpus:** `rag_corpus_mode` + ingest scripts — add tenant-specific RAG without pipeline changes.
- **API integration:** REST-ready ticket store; SMTP notification hooks; Gemini client is thin HTTP — replace with Azure OpenAI / local Ollama adapter.
- **Multi-tenant:** department taxonomy in `departments.py`; Chroma collection per tenant (path config).

## Reports

- `test-reports/master_report.html` — grand assessment
- `test-reports/judge50_report.html` — Nasscom firm-specific set
- `docs/CODE_WALKTHROUGH.md` — pipeline map

Run: `python scripts/master_assessment.py --live`
