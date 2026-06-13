#!/usr/bin/env python3
"""Patch synthetic RAG ticket titles with demo assignee names (600+ tickets)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "synthetic" / "tickets_1000.json"

# Department → demo agent display names (must match seed_users / demo_profiles)
DEPT_ASSIGNEES: dict[str, list[str]] = {
    "Hardware": ["Sree", "Kiran", "Vikram"],
    "Software": ["Subbu", "Sruthi", "Meena", "Anita"],
    "Network": ["Shashi", "Rahul", "Deepak"],
    "SecOps": ["Narsimha", "Chandana", "Rohan"],
    "Access Management": ["Satya", "Meera"],
    "Identity": ["Satya", "Meera"],
    "DBA": ["Sagar", "Priya", "Arjun"],
    "Storage": ["Sagar", "Priya", "Arjun"],
}

# Legacy hand-picked high-signal titles (kept for stable demo references)
TITLE_PATCHES: dict[str, str] = {
    "syn-0002": "Printer paper jam Floor 6 — Sree (Hardware) resolved",
    "syn-0015": "Docker hypervisor error — escalated to Sree hardware team",
    "syn-0153": "Chrome slow after update — Subbu Software assist",
    "syn-0161": "SharePoint upload denied — Subbu application support",
    "syn-0210": "Outlook profile stuck loading — Sruthi software queue",
    "syn-0198": "Outlook search returns nothing — Sruthi team ticket",
    "syn-0719": "Wi-Fi certificate trust issue — Shashi Network queue",
    "syn-0727": "VPN error 807 cannot connect — Shashi network team",
    "syn-0289": "AWS access key exposed on GitHub — Narsimha SecOps",
    "syn-0294": "Phishing credential harvest — Narsimha SecOps H3",
    "syn-0311": "Spear-phishing report — Chandana SecOps specialist",
    "syn-0302": "GitLab CI secret in log — Chandana security desk",
    "syn-0866": "Forgot portal password — Satya Access Management",
    "syn-0917": "New hire AD provisioning — Satya identity team",
    "syn-0578": "Veeam backup archive failed — Sagar DBA queue",
    "syn-0607": "SQL transaction log full — Sagar database team",
}

_ASSIGNEE_IN_TITLE = re.compile(
    r"\b(Sree|Kiran|Vikram|Subbu|Sruthi|Meena|Anita|Shashi|Rahul|Deepak|"
    r"Narsimha|Chandana|Rohan|Satya|Meera|Sagar|Priya|Arjun)\b",
    re.I,
)


def _pick_assignee(ticket_id: str, department: str) -> str:
    names = DEPT_ASSIGNEES.get(department) or DEPT_ASSIGNEES.get("Software", ["Subbu"])
    idx = int(ticket_id.split("-")[-1]) % len(names)
    return names[idx]


def _title_with_assignee(title: str, assignee: str, department: str) -> str:
    if _ASSIGNEE_IN_TITLE.search(title):
        return title
    short_dept = department.replace("Access Management", "Access Mgmt")
    return f"{title} — {assignee} ({short_dept}) resolved"


def main() -> int:
    if not CORPUS.exists():
        print(f"Missing {CORPUS}", file=sys.stderr)
        return 1

    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    changed = 0
    already_named = 0

    for ticket in data["tickets"]:
        tid = ticket["id"]
        if tid in TITLE_PATCHES:
            new_title = TITLE_PATCHES[tid]
        else:
            dept = ticket.get("department") or "Software"
            assignee = _pick_assignee(tid, dept)
            new_title = _title_with_assignee(ticket["title"], assignee, dept)

        if _ASSIGNEE_IN_TITLE.search(ticket["title"]):
            already_named += 1
        if ticket["title"] != new_title:
            ticket["title"] = new_title
            changed += 1

    CORPUS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    total_named = sum(
        1 for t in data["tickets"] if _ASSIGNEE_IN_TITLE.search(t["title"])
    )
    print(f"Patched {changed} title(s); {total_named}/1000 include assignee names")
    print("Re-run: python scripts/ingest_synthetic_corpus.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
