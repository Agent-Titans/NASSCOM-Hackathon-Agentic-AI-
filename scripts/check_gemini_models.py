#!/usr/bin/env python3
"""List and smoke-test Gemini models using .env (never commit .env)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    path = Path(__file__).resolve().parents[1] / ".env"
    if not path.exists():
        print("Missing .env — copy .env.example and set GOOGLE_API_KEY")
        sys.exit(1)
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def main() -> None:
    env = load_env()
    key = env.get("GOOGLE_API_KEY", "")
    if not key:
        print("GOOGLE_API_KEY is empty in .env")
        sys.exit(1)

    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    with urllib.request.urlopen(list_url, timeout=20) as r:
        data = json.loads(r.read().decode())

    gen = [
        m["name"].replace("models/", "")
        for m in data.get("models", [])
        if "generateContent" in m.get("supportedGenerationMethods", [])
    ]
    emb = [
        m["name"].replace("models/", "")
        for m in data.get("models", [])
        if "embedContent" in m.get("supportedGenerationMethods", [])
    ]
    print("Generate-capable (flash/lite subset):")
    for name in sorted(gen):
        if "flash" in name.lower() or "lite" in name.lower():
            print(f"  - {name}")
    print("\nEmbed-capable:")
    for name in sorted(emb):
        print(f"  - {name}")

    for label, model, kind in [
        ("CLASSIFY", env.get("GEMINI_MODEL_CLASSIFY", "gemini-2.5-flash"), "gen"),
        ("RESOLVE", env.get("GEMINI_MODEL_RESOLVE", "gemini-2.5-flash"), "gen"),
        ("EMBED", env.get("GEMINI_MODEL_EMBED", "gemini-embedding-001"), "emb"),
    ]:
        if kind == "gen":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            body = json.dumps(
                {"contents": [{"parts": [{"text": 'Reply: {"ok":true}'}]}]}
            ).encode()
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={key}"
            body = json.dumps(
                {
                    "model": f"models/{model}",
                    "content": {"parts": [{"text": "smoke test"}]},
                }
            ).encode()
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                json.loads(r.read().decode())
            print(f"\n{label} ({model}): OK")
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            print(f"\n{label} ({model}): FAIL — {err}")


if __name__ == "__main__":
    main()
