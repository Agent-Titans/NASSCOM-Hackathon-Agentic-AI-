# Judge & teammate setup

**Start here:** [`COLLEAGUE_SETUP.md`](COLLEAGUE_SETUP.md) — full clone-to-demo guide for colleagues.

Quick commands:

```bash
bash scripts/setup_venv.sh && source .venv/bin/activate
cp .env.example .env   # add GOOGLE_API_KEY
python scripts/bootstrap_rag_environment.py
bash scripts/run_app.sh
```

- Password: `1234` · Accounts: `docs/COLLEAGUE_SETUP.md`
- Demo script: `docs/DEMO_CHECKLIST.md`
- Routing reports: `test-reports/index.html`
- RAG corpus CSV: `data/synthetic/tickets_1000.csv`

**Before sharing the repo** (maintainer): `bash scripts/prepare_handoff.sh` — clears live UI tickets, keeps Chroma + 1k syn corpus.
