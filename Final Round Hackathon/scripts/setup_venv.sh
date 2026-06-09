#!/usr/bin/env bash
# Prefer Python 3.10+ for full AI stack (google-generativeai).
set -e
cd "$(dirname "$0")/.."

PY=""
for cmd in /usr/local/bin/python3.11 /opt/homebrew/bin/python3.11 python3.12 python3.11 python3.10 python3; do
  if command -v "$cmd" >/dev/null 2>&1; then
    if "$cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PY=$cmd
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  echo "Need Python 3.10+. Install: brew install python@3.11"
  exit 1
fi

echo "Using $PY ($($PY --version))"
rm -rf .venv
"$PY" -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-ai.txt
echo "Done. Activate: source .venv/bin/activate"
