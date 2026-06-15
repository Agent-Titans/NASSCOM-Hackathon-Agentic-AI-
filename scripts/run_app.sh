#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  bash scripts/setup_venv.sh
fi
source .venv/bin/activate
python scripts/init_db.py
python scripts/seed_users.py
# macOS: disable FSEvents file watcher (avoids Streamlit exit 134 on some Macs)
streamlit run src/ui/app.py --server.fileWatcherType none
