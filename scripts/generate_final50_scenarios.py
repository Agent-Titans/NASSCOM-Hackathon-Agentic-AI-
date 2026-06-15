#!/usr/bin/env python3
"""
Generate data/set_final50_scenarios.json — 50 unique Nasscom final eval tickets.

Each case carries its own expect {hand, department, category} aligned to title/description
(Demo20/Clear50 style). No positional DEPT_PLAN template.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "set_final50_scenarios.json"

FIRMS = (
    ("AM", "Amazon"),
    ("GO", "Google"),
    ("DL", "Deloitte"),
    ("NK", "Nike"),
    ("TS", "Tesla"),
)


class Scenario(NamedTuple):
    title: str
    description: str
    hand: str
    department: str
    category: str
    acceptable_hands: list[str]
    urgency: str


def _h(hand: str) -> list[str]:
    if hand == "3":
        return ["3"]
    if hand == "1":
        return ["1", "2"]
    return ["2"]


TEMPLATES: dict[str, list[Scenario]] = {
    "Amazon": [
        Scenario(
            "Seller Central listing upload API errors",
            "Amazon Seller Central bulk listing upload API returns HTTP 503 for India marketplace sellers. Peak sale event starts in 2 hours.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "AWS WorkSpaces client disconnect loop on macOS",
            "AWS WorkSpaces client disconnects every 5 minutes on macOS Sonoma. Remote merchandising team cannot access catalog tools.",
            "2", "Application", "Application", ["2"], "high",
        ),
        Scenario(
            "Redshift cluster disk full on analytics schema",
            "Amazon Redshift RA3 cluster disk full on analytics schema. Nightly ETL for demand forecast failing.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Aurora PostgreSQL read replica lag critical",
            "Aurora PostgreSQL read replica lag exceeds 15 minutes on order pipeline. Checkout microservice reading stale inventory.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Forgot password on internal retail portal",
            "Forgot password on internal Amazon retail associate portal. Account locked after failed attempts. Shift starts in 30 minutes.",
            "1", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "MFA device lost — cannot access vendor portal",
            "Lost phone with Authenticator app for vendor portal MFA. Need temporary access to approve PO workflow.",
            "2", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "Direct Connect BGP flapping to us-east-1",
            "AWS Direct Connect BGP session flapping between corporate DC and us-east-1. Latency spikes on fulfillment APIs.",
            "2", "Network", "Network", _h("2"), "high",
        ),
        Scenario(
            "Corporate VPN split tunnel blocks internal wiki",
            "Amazon corporate VPN split tunnel policy blocks internal wiki host. New hire onboarding docs unreachable from home.",
            "2", "Network", "Network", _h("1"), "medium",
        ),
        Scenario(
            "Warehouse Zebra scanner Wi-Fi roaming drops",
            "Zebra handheld scanners lose Wi-Fi when roaming between fulfillment center AP zones. Pick path delays increasing.",
            "2", "Network", "Network", _h("2"), "medium",
        ),
        Scenario(
            "Security incident: exposed S3 bucket with customer PII",
            "Security incident: public S3 bucket discovered containing customer PII export. Bucket policy shows world-readable ACL.",
            "3", "SecOps", "Security", _h("3"), "critical",
        ),
    ],
    "Google": [
        Scenario(
            "Gmail delegated inbox sync stopped for exec assistant",
            "Gmail delegated inbox stopped syncing for executive assistant account. Calendar invites not appearing.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Google Meet live stream fails for all-hands",
            "Google Meet live stream encoder fails 10 minutes before APAC all-hands. 4000 employees waiting.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "BigQuery scheduled query slot exhaustion",
            "BigQuery on-demand slots exhausted for marketing attribution scheduled query. Campaign ROI dashboard stale.",
            "2", "Database", "Database", _h("2"), "high",
        ),
        Scenario(
            "Cloud Spanner transaction aborted rate spike",
            "Cloud Spanner transaction aborted rate spike on identity service. Login error budget burning.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Cloud SQL MySQL replication broken after upgrade",
            "Cloud SQL MySQL cross-region replica replication broken after maintenance upgrade. Read traffic failing over.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Workspace admin locked out after role change",
            "Google Workspace super admin locked out after accidental OU role change. Cannot reset via recovery admin.",
            "2", "Access Management", "Access Management", _h("1"), "high",
        ),
        Scenario(
            "BeyondCorp access denied for new contractor",
            "BeyondCorp access denied for new contractor on ChromeOS. Zero-trust policy shows device not compliant.",
            "2", "Access Management", "Access Management", _h("2"), "medium",
        ),
        Scenario(
            "Inter-VPC firewall rule blocking Pub/Sub",
            "New VPC firewall rule blocking Pub/Sub push subscription to Cloud Run. Event pipeline backlog growing.",
            "2", "Network", "Network", _h("2"), "high",
        ),
        Scenario(
            "Office Wi-Fi 802.1X certificate expired",
            "Bangalore office Wi-Fi 802.1X radius certificate expired. Hundreds of engineers on guest network only.",
            "2", "Network", "Network", _h("2"), "medium",
        ),
        Scenario(
            "Security incident: service account key in public repo",
            "Security incident: GCP service account JSON key found in public GitHub fork. Key has storage admin scope.",
            "3", "SecOps", "Security", _h("3"), "critical",
        ),
    ],
    "Deloitte": [
        Scenario(
            "SAP Fiori tile timeout for audit workflow",
            "SAP Fiori approve-audit tile times out for EMEA consultants. Month-end sign-off deadline today.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Workday time entry not submitting",
            "Workday time entry page spins on submit for offshore team. Payroll extract runs tonight.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Tableau Server extract refresh failed",
            "Tableau Server extract refresh failed on client utilization workbook. Partner review meeting in 1 hour.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "SQL Server AG failover group not synchronizing",
            "SQL Server availability group secondary not synchronizing after patch Tuesday. Reporting DB read-only.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Oracle audit vault agent offline",
            "Oracle Audit Vault agent offline on finance DB host. Compliance scan window open.",
            "2", "Database", "Database", _h("2"), "high",
        ),
        Scenario(
            "Password reset for client VPN portal",
            "Forgot password for Deloitte client VPN portal. Need access to shared engagement folder.",
            "1", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "Smart card PIN locked on engagement laptop",
            "PIV smart card PIN locked on engagement laptop. Cannot authenticate to client VDI.",
            "2", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "Client site MPLS circuit down — no RDP",
            "MPLS circuit to client site down. Team cannot RDP to client jump server for go-live.",
            "2", "Network", "Network", _h("2"), "critical",
        ),
        Scenario(
            "Conference room AV controller offline",
            "Video conference room AV controller offline on 14th floor. Client workshop starting.",
            "2", "Infrastructure", "Infrastructure", _h("2"), "medium",
        ),
        Scenario(
            "Security incident: phishing report with malware attachment",
            "Security incident: user reported phishing email with macro-enabled attachment opened. Endpoint isolation requested.",
            "3", "SecOps", "Security", _h("3"), "critical",
        ),
    ],
    "Nike": [
        Scenario(
            "SAP retail POS integration timeout",
            "SAP CAR POS integration timeout at outlet stores. End-of-day sales upload failing.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Adobe Creative Cloud license not provisioning",
            "Adobe Creative Cloud license not provisioning for design team. Campaign asset deadline tomorrow.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Snowflake warehouse suspend blocking BI job",
            "Snowflake virtual warehouse auto-suspend blocking overnight BI job. Inventory dashboard outdated.",
            "2", "Database", "Database", _h("2"), "high",
        ),
        Scenario(
            "MongoDB Atlas cluster CPU throttling",
            "MongoDB Atlas M30 cluster CPU throttling on product catalog API. Mobile app search slow.",
            "2", "Database", "Database", _h("2"), "high",
        ),
        Scenario(
            "Okta SSO loop on employee benefits portal",
            "Okta SSO redirect loop on employee benefits portal after password change.",
            "2", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "New hire AD account not syncing to Mac login",
            "New hire Active Directory account not syncing to Mac login. Cannot access Nike network drives.",
            "2", "Access Management", "Access Management", _h("2"), "medium",
        ),
        Scenario(
            "GlobalProtect VPN error 619 on travel",
            "GlobalProtect VPN error 619 connecting from hotel Wi-Fi. Remote designer blocked from PLM.",
            "2", "Network", "Network", _h("2"), "high",
        ),
        Scenario(
            "DNS failure for internal sample tracking app",
            "Internal sample tracking app DNS record points to retired server. Factory line using paper log.",
            "2", "Network", "Network", _h("2"), "medium",
        ),
        Scenario(
            "Label printer offline on distribution center line 4",
            "Zebra label printer offline on distribution center line 4. Carton routing labels not printing.",
            "2", "Infrastructure", "Infrastructure", _h("2"), "medium",
        ),
        Scenario(
            "Security incident: ransomware alert on file server",
            "Security incident: Defender ransomware alert on regional marketing file server. Shares offline.",
            "3", "SecOps", "Security", _h("3"), "critical",
        ),
    ],
    "Tesla": [
        Scenario(
            "MES workstation HMI freeze on Gigafactory line",
            "Manufacturing execution HMI freezes on Gigafactory battery line. Operators cannot acknowledge quality holds.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "Factory CAD viewer crash after GPU driver update",
            "Factory floor CAD viewer crashes after NVIDIA driver push. Maintenance cannot open station diagrams.",
            "2", "Application", "Application", _h("2"), "high",
        ),
        Scenario(
            "InfluxDB time-series gap on weld telemetry",
            "InfluxDB gap in weld telemetry stream. Quality analytics missing last 6 hours of data.",
            "2", "Database", "Database", _h("2"), "high",
        ),
        Scenario(
            "PostgreSQL connection pool exhausted on logistics API",
            "PostgreSQL connection pool exhausted on parts logistics API. AGV routing commands timing out.",
            "2", "Database", "Database", _h("2"), "critical",
        ),
        Scenario(
            "Contractor badge not activating for plant access",
            "Contractor physical badge not activating at plant turnstile. Safety induction completed but access denied.",
            "2", "Access Management", "Access Management", _h("2"), "medium",
        ),
        Scenario(
            "RSA token out of sync after phone replacement",
            "RSA SecurID token out of sync after mobile device replacement. Cannot login to plant SCADA read-only.",
            "1", "Access Management", "Access Management", _h("1"), "medium",
        ),
        Scenario(
            "Plant floor VLAN isolation blocking PLC historian",
            "New VLAN segmentation blocking PLC historian collector. Engineering cannot trend oven temperatures.",
            "2", "Network", "Network", _h("2"), "high",
        ),
        Scenario(
            "5G private network handoff drops on mobile tablets",
            "Private 5G handoff drops for quality inspection tablets moving between zones.",
            "2", "Network", "Network", _h("2"), "medium",
        ),
        Scenario(
            "NAS snapshot replication lag for engineering shares",
            "Engineering NAS snapshot replication lag exceeds 24 hours. Design branch worried about RPO.",
            "2", "Storage", "Storage", _h("2"), "high",
        ),
        Scenario(
            "Security incident: unauthorized Modbus write attempt",
            "Security incident: IDS alert for unauthorized Modbus write attempt on paint line controller.",
            "3", "SecOps", "Security", _h("3"), "critical",
        ),
    ],
}


def build_cases() -> list[dict]:
    cases: list[dict] = []
    for prefix, firm in FIRMS:
        for i, sc in enumerate(TEMPLATES[firm], 1):
            cases.append(
                {
                    "id": f"{prefix}{i:02d}",
                    "firm": firm,
                    "title": sc.title,
                    "description": sc.description,
                    "urgency": sc.urgency,
                    "expect": {
                        "hand": sc.hand,
                        "department": sc.department,
                        "category": sc.category,
                    },
                    "acceptable_hands": sc.acceptable_hands,
                    "notes": f"{firm} · {sc.department}",
                }
            )
    return cases


def main() -> int:
    cases = build_cases()
    payload = {
        "version": 2,
        "description": (
            "Final50 — 50 unique Nasscom evaluation tickets (Amazon, Google, Deloitte, Nike, Tesla). "
            "Per-ticket gold labels aligned to content. Zero overlap with Demo20/Clear50."
        ),
        "firms": [f[1] for f in FIRMS],
        "cases": cases,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
