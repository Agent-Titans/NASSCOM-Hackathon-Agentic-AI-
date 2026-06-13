#!/usr/bin/env bash
# Prepare repo for colleague handoff — live tickets cleared, Chroma intact locally.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "=== 1. Clear live UI tickets (keep syn-* + Chroma) ==="
python scripts/clean_for_ui_demo.py

echo ""
echo "=== 2. Verify environment ==="
python -c "
from src.db.session import get_session_factory, init_db
from src.db.models import Ticket
from src.stores.chroma_store import ChromaTicketStore
from src.config.settings import get_settings
init_db()
s = get_session_factory()()
live = s.query(Ticket).filter(~Ticket.ticket_id.like('syn-%')).count()
syn = s.query(Ticket).filter(Ticket.ticket_id.like('syn-%')).count()
c = ChromaTicketStore()
cfg = get_settings()
assert live == 0, f'Expected 0 live tickets, got {live}'
print(f'OK  live={live} syn={syn} chroma={c.count} email={cfg.email_notifications_enabled}')
"

echo ""
echo "=== 3. Colleague clone steps (on new machine) ==="
cat <<'EOF'
  git clone <repo-url>
  cd "Final Round Hackathon"
  bash scripts/setup_venv.sh && source .venv/bin/activate
  cp .env.example .env    # add GOOGLE_API_KEY
  python scripts/bootstrap_rag_environment.py
  bash scripts/run_app.sh
  # Password: 1234 — see docs/COLLEAGUE_SETUP.md
EOF

echo ""
echo "Handoff ready. Chroma is local-only (gitignored); colleague runs bootstrap to build it."
