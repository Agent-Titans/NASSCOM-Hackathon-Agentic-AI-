#!/usr/bin/env python3
"""Assemble 50-ticket master suite — one clear scenario per firm."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "set_master50_scenarios.json"

# (source file, firm label, case id to pick) — 50 distinct firms
PICKS: list[tuple[str, str, str]] = [
    ("set_capgemini50_scenarios.json", "Capgemini", "CG01"),
    ("set_capgemini50_scenarios.json", "Accenture", "CG02"),
    ("set_jpmorgan_tech30_scenarios.json", "JP Morgan", "JP01"),
    ("set_jpmorgan_tech30_scenarios.json", "Goldman Sachs", "JP05"),
    ("set_hsbc_india20_scenarios.json", "HSBC India", "HI01"),
    ("set_hsbc_india20_scenarios.json", "Standard Chartered", "HI05"),
    ("set_tcs_final30_scenarios.json", "TCS", "TC01"),
    ("set_tcs_final30_scenarios.json", "Infosys", "TC08"),
    ("set_nasscom20_scenarios.json", "NASSCOM", "NS01"),
    ("set_nasscom20_scenarios.json", "Wipro", "NS05"),
    ("set_microsoft20_scenarios.json", "Microsoft", "MS01"),
    ("set_microsoft20_scenarios.json", "Amazon AWS", "MS08"),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "HCL Tech", "MX01"),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "Deloitte", "MX05"),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "Nvidia", "MX12"),
    ("set_software_office30_scenarios.json", "Software Office", "SW01"),
    ("set_software_office30_scenarios.json", "Google Workspace", "SW05"),
    ("set_aa20_scenarios.json", "Cognizant", "A01"),
    ("set_aa20_scenarios.json", "LTIMindtree", "A08"),
    ("set_w20_scenarios.json", "IBM", "W01"),
    ("set_w20_scenarios.json", "Oracle", "W10"),
    ("set_x25_scenarios.json", "SAP", "X01"),
    ("set_x25_scenarios.json", "Salesforce", "X10"),
    ("set_y10_scenarios.json", "ServiceNow", "Y01"),
    ("set_z10_scenarios.json", "Adobe", "Z01"),
    ("set_mixed15_scenarios.json", "Flipkart", "MX01"),
    ("set_capgemini50_scenarios.json", "EY", "CG10"),
    ("set_capgemini50_scenarios.json", "KPMG", "CG15"),
    ("set_capgemini50_scenarios.json", "PwC", "CG20"),
    ("set_jpmorgan_tech30_scenarios.json", "Barclays", "JP10"),
    ("set_jpmorgan_tech30_scenarios.json", "Citibank", "JP15"),
    ("set_hsbc_india20_scenarios.json", "ICICI Bank", "HI08"),
    ("set_hsbc_india20_scenarios.json", "HDFC Bank", "HI12"),
    ("set_tcs_final30_scenarios.json", "Tech Mahindra", "TC15"),
    ("set_tcs_final30_scenarios.json", "Persistent", "TC20"),
    ("set_nasscom20_scenarios.json", "Zoho", "NS10"),
    ("set_nasscom20_scenarios.json", "Freshworks", "NS15"),
    ("set_microsoft20_scenarios.json", "LinkedIn", "MS12"),
    ("set_microsoft20_scenarios.json", "GitHub", "MS15"),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "Intel", "MX08"),
    ("set_mixed_wipro_hcl_deloitte_nvidia20_scenarios.json", "AMD", "MX15"),
    ("set_software_office30_scenarios.json", "Slack", "SW10"),
    ("set_software_office30_scenarios.json", "Zoom", "SW15"),
    ("set_aa20_scenarios.json", "Mphasis", "A12"),
    ("set_w20_scenarios.json", "Red Hat", "W15"),
    ("set_x25_scenarios.json", "Atlassian", "X15"),
    ("set_capgemini50_scenarios.json", "Boeing IT", "CG25"),
    ("set_jpmorgan_tech30_scenarios.json", "Morgan Stanley", "JP20"),
    ("set_tcs_final30_scenarios.json", "Cisco", "TC25"),
    ("set_nasscom20_scenarios.json", "Paytm", "NS18"),
]


def _load_by_id(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data["cases"]}


def main() -> int:
    cases: list[dict] = []
    seen_firms: set[str] = set()

    for filename, firm, case_id in PICKS:
        if firm in seen_firms:
            continue
        path = ROOT / "data" / filename
        if not path.exists():
            print(f"Skip missing {path}")
            continue
        by_id = _load_by_id(path)
        if case_id not in by_id:
            case_id = next(iter(by_id))
        item = deepcopy(by_id[case_id])
        item["firm"] = firm
        item["source_id"] = item["id"]
        cases.append(item)
        seen_firms.add(firm)
        if len(cases) >= 50:
            break

    if len(cases) < 50:
        raise SystemExit(f"Expected 50 cases, got {len(cases)}")

    for i, case in enumerate(cases, start=1):
        case["id"] = f"F{i:02d}"

    out = {
        "version": 1,
        "description": (
            "Master 50 — one clear scenario per firm "
            "(50 distinct enterprises, unambiguous titles & descriptions)"
        ),
        "cases": cases,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(cases)} cases, {len(seen_firms)} firms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
