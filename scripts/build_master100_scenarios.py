#!/usr/bin/env python3
"""Assemble 100-ticket master scenario suite from past firm test sets."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "set_master100_scenarios.json"

# (source file, firm label, count)
SLICES: list[tuple[str, str, int]] = [
    ("set_capgemini50_scenarios.json", "Capgemini", 20),
    ("set_jpmorgan_tech30_scenarios.json", "JP Morgan", 15),
    ("set_hsbc_india20_scenarios.json", "HSBC India", 15),
    ("set_tcs_final30_scenarios.json", "TCS", 12),
    ("set_nasscom20_scenarios.json", "NASSCOM", 10),
    ("set_microsoft20_scenarios.json", "Microsoft", 10),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "Wipro/HCL/Deloitte/Nvidia", 10),
    ("set_software_office30_scenarios.json", "Software Office", 8),
]


def main() -> int:
    cases: list[dict] = []
    for filename, firm, count in SLICES:
        path = ROOT / "data" / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data["cases"][:count]:
            item = deepcopy(row)
            item["firm"] = firm
            item["source_id"] = item["id"]
            cases.append(item)

    if len(cases) != 100:
        raise SystemExit(f"Expected 100 cases, got {len(cases)}")

    for i, case in enumerate(cases, start=1):
        case["id"] = f"M{i:03d}"

    out = {
        "version": 1,
        "description": (
            "Master 100 — multi-firm routing validation "
            "(Capgemini, JP Morgan, HSBC, TCS, NASSCOM, Microsoft, "
            "Wipro/HCL/Deloitte/Nvidia, Software Office)"
        ),
        "cases": cases,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(cases)} cases)")
    firms = {}
    for c in cases:
        firms[c["firm"]] = firms.get(c["firm"], 0) + 1
    for name, n in firms.items():
        print(f"  {name}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
