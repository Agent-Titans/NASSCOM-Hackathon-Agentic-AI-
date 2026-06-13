# Synthetic RAG corpus

| File | Description |
|------|-------------|
| `tickets_1000.json` | Source of truth — 1,000 RESOLVED enterprise tickets (committed) |
| `tickets_1000.csv` | Same data in CSV — open in Excel / Google Sheets |

**Regenerate CSV after editing JSON:**

```bash
python scripts/export_synthetic_corpus_csv.py
```

**Rebuild vector index (after JSON changes):**

```bash
python scripts/ingest_synthetic_corpus.py
```

Sixteen titles include demo assignee names (Sree, Subbu, Shashi, Narsimha, etc.) for realistic retrieval during agent demos.
