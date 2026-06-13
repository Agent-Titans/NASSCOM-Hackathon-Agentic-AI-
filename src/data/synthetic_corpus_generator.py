"""
Generate 1,000 synthetic resolved tickets aligned to Use Case 1 taxonomy.

Output schema matches data/synthetic/tickets_1000.json — used for RAG ingest.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

from src.data.rag_demo_corpus import department_for_category

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "synthetic" / "tickets_1000.json"

USE_CASE_CATEGORIES: tuple[str, ...] = (
    "Infrastructure",
    "Application",
    "Security",
    "Database",
    "Storage",
    "Network",
    "Access Management",
)

# (title_tpl, description_tpl, resolution_steps)
_TEMPLATES: dict[str, dict[str, list[tuple[str, str, list[str]]]]] = {
    "Infrastructure": {
        "1": [
            (
                "Printer paper jam on floor {n}",
                "Printer paper jammed in {n}nd floor office printer. Toner OK, red jam light on.",
                [
                    "Open the front panel and remove jammed sheets gently.",
                    "Check the rear duplexer for torn paper fragments.",
                    "Run a test print from the device panel.",
                ],
            ),
            (
                "Laptop battery not charging",
                "Laptop charger plugged in but battery stuck at {n}%. No charging light.",
                [
                    "Reseat power adapter and try another wall outlet.",
                    "Hard-reset: shut down, hold power 30 seconds, reboot.",
                    "Update battery driver from vendor support site.",
                ],
            ),
        ],
        "2": [
            (
                "Docker Desktop hypervisor error",
                "Docker Desktop failing to start with hypervisor error after BIOS update.",
                [
                    "Enable VT-x/AMD-V in BIOS settings.",
                    "Disable conflicting hypervisors (VirtualBox/WSL1).",
                    "Reinstall Docker Desktop with admin rights.",
                ],
            ),
            (
                "Laptop fan loud after update",
                "Laptop fan running loud and hot after Windows update build {n}.",
                [
                    "Check Task Manager for runaway CPU processes.",
                    "Clear dust from vents; verify thermal paste if under warranty.",
                    "Rollback recent kernel/driver update if issue started immediately.",
                ],
            ),
        ],
        "3": [
            (
                "Suspected hardware tampering",
                "Workstation case seal broken; unknown USB device found inserted overnight.",
                [
                    "Isolate device from network immediately.",
                    "Escalate to SecOps for forensic imaging.",
                    "Do not power off until specialist advises.",
                ],
            ),
        ],
    },
    "Application": {
        "1": [
            (
                "Chrome slow after update",
                "Google Chrome spins on every site after Windows update. Other browsers OK.",
                [
                    "Clear browser cache and disable extensions.",
                    "Reset Chrome settings to default.",
                    "Reinstall Chrome from official package.",
                ],
            ),
            (
                "Outlook stuck on loading profile",
                "Outlook hangs on loading profile for user mailbox {n}.",
                [
                    "Start Outlook in safe mode (outlook.exe /safe).",
                    "Create new Outlook profile and re-add account.",
                    "Repair Office installation from Control Panel.",
                ],
            ),
        ],
        "2": [
            (
                "SharePoint upload permission denied",
                "Cannot upload files to SharePoint team site — permission denied on library {n}.",
                [
                    "Verify user has Contribute on the document library.",
                    "Check if site is in read-only or retention hold.",
                    "Re-sync OneDrive client and retry upload.",
                ],
            ),
            (
                "SAP GUI session timeout",
                "SAP GUI disconnects every {n} minutes with RFC_ERROR.",
                [
                    "Increase SAP GUI idle timeout per policy.",
                    "Check VPN stability and MTU settings.",
                    "Clear local SAP GUI cache and reapply patches.",
                ],
            ),
        ],
        "3": [
            (
                "Vague application error",
                "Application shows weird error — user did not capture message. Intermittent.",
                [
                    "Schedule live triage to capture screenshot.",
                    "Enable verbose client logging.",
                    "Route to app owner after symptoms confirmed.",
                ],
            ),
        ],
    },
    "Security": {
        "3": [
            (
                "AWS access key exposed on GitHub",
                "Raw AWS secret access key pushed to public GitHub branch repo-{n}.",
                [
                    "Rotate compromised key immediately in IAM.",
                    "Invalidate active sessions using the key.",
                    "Run secret scan and open SecOps incident.",
                ],
            ),
            (
                "VPN unauthorized access alert",
                "Possible unauthorized VPN access detected on admin account from unknown geo.",
                [
                    "Disable affected VPN account pending review.",
                    "Collect authentication logs for last 24 hours.",
                    "SecOps to verify travel policy and MFA status.",
                ],
            ),
            (
                "Phishing report — credential harvest",
                "User reported phishing email asking for O365 password on fake login page.",
                [
                    "Quarantine sender domain at email gateway.",
                    "Force password reset if user submitted credentials.",
                    "Publish awareness alert for similar lures.",
                ],
            ),
        ],
    },
    "Database": {
        "1": [
            (
                "Read-only database user request",
                "Need read-only SQL access to reporting database {n} for analytics.",
                [
                    "Submit data access request with manager approval.",
                    "DBA creates read-only login on reporting replica.",
                    "User tests connection via approved SQL client.",
                ],
            ),
        ],
        "2": [
            (
                "SQL null values after migration",
                "Production SQL table returns NULL in column after migration script {n}.",
                [
                    "Compare source and target row counts.",
                    "Review migration script for nullable column mapping.",
                    "DBA to run validation query and backfill if safe.",
                ],
            ),
            (
                "DB2 Cognos connection failure",
                "IBM Cognos cannot connect to DB2 — configure connection details for framework manager.",
                [
                    "Verify DB2 listener and firewall rules.",
                    "Test JDBC URL from Cognos gateway server.",
                    "Update datasource credentials in Cognos admin.",
                ],
            ),
        ],
        "3": [
            (
                "Suspected SQL injection attempt",
                "Web app logs show SQL injection patterns in query parameter id={n}.",
                [
                    "Enable WAF block rule for observed payload.",
                    "Review application parameterized queries.",
                    "SecOps and DBA joint incident review.",
                ],
            ),
        ],
    },
    "Storage": {
        "1": [
            (
                "NAS share quota warning",
                "NAS share quota at {n}% — backup jobs may fail tonight.",
                [
                    "Archive old project folders per retention policy.",
                    "Request temporary quota increase if justified.",
                    "Re-run backup after freeing space.",
                ],
            ),
        ],
        "2": [
            (
                "Storage backup failed — archive job",
                "Storage backup failed last night. NAS share quota may be full. Disk archive job error.",
                [
                    "Check NAS connectivity and credentials.",
                    "Purge expired archives per policy.",
                    "Retry backup job and verify checksum.",
                ],
            ),
            (
                "SAN LUN offline",
                "SAN LUN for file cluster {n} shows offline in storage console.",
                [
                    "Verify fibre-channel link and zoning.",
                    "Failover to secondary path if available.",
                    "Engage storage vendor if hardware fault suspected.",
                ],
            ),
        ],
        "3": [
            (
                "Ransomware indicator on file share",
                "Multiple files renamed with unknown extension on finance share.",
                [
                    "Isolate affected NAS snapshot from network.",
                    "Do not pay ransom; engage SecOps immediately.",
                    "Restore from immutable backup after forensics.",
                ],
            ),
        ],
    },
    "Network": {
        "1": [
            (
                "VPN error 807",
                "Error 807 when starting corporate VPN client after laptop sleep.",
                [
                    "Disable fast startup in Windows power settings.",
                    "Reinstall VPN client with latest package.",
                    "Verify UDP 500/4500 not blocked on local network.",
                ],
            ),
            (
                "Wi-Fi certificate trust issue",
                "Corporate Wi-Fi prompts untrusted certificate on floor {n}.",
                [
                    "Install updated root CA from IT portal.",
                    "Forget and rejoin SSID.",
                    "Confirm device is on corporate MDM profile.",
                ],
            ),
        ],
        "2": [
            (
                "IP whitelist for SQL access",
                "Need IP {n}.x whitelisted to reach SQL database from home office.",
                [
                    "Submit firewall change with business justification.",
                    "Network team adds rule to database security group.",
                    "User verifies connectivity after change window.",
                ],
            ),
            (
                "Intermittent packet loss to datacenter",
                "Ping loss {n}% to primary datacenter during business hours.",
                [
                    "Collect traceroute from affected sites.",
                    "Check ISP circuit utilization and errors.",
                    "Schedule maintenance if core switch port errors rise.",
                ],
            ),
        ],
        "3": [
            (
                "Possible DDoS on perimeter",
                "Perimeter firewall shows SYN flood spike on public API {n}.",
                [
                    "Enable rate limiting and geo block if approved.",
                    "Notify SecOps and application owner.",
                    "Scale edge protection per runbook.",
                ],
            ),
        ],
    },
    "Access Management": {
        "1": [
            (
                "Forgot portal password",
                "Forgot password and cannot login to company portal. Need AD password reset link.",
                [
                    "Open self-service password portal.",
                    "Complete MFA verification via registered device.",
                    "Set new password meeting complexity policy.",
                ],
            ),
            (
                "MFA authenticator not working",
                "Authenticator app codes rejected at login after phone replacement.",
                [
                    "Use backup codes if available.",
                    "Contact Identity to reset MFA enrollment.",
                    "Re-register authenticator on new device.",
                ],
            ),
        ],
        "2": [
            (
                "New hire account provisioning",
                "New employee start date {n} — need O365 and VPN accounts.",
                [
                    "Verify HR onboarding ticket approved.",
                    "Create AD account and assign base groups.",
                    "Send welcome email with MFA enrollment steps.",
                ],
            ),
            (
                "Role change — application access",
                "User transferred to team {n}; needs Salesforce and Jira access.",
                [
                    "Manager approves entitlement change.",
                    "Remove old team groups; add new role groups.",
                    "User confirms access within 24 hours.",
                ],
            ),
        ],
        "3": [
            (
                "Privilege escalation request ambiguous",
                "User requests admin access to production but scope unclear.",
                [
                    "Identity interview to confirm systems and duration.",
                    "Require manager + app owner approval.",
                    "Grant time-bound PIM role if policy allows.",
                ],
            ),
        ],
    },
}

_HAND_WEIGHTS: dict[str, tuple[tuple[str, int], ...]] = {
    "Security": (("3", 100),),
    "default": (("1", 40), ("2", 45), ("3", 15)),
}

_PRIORITY_WEIGHTS = ("P0", "P1", "P2")
_PRIORITY_W = (2, 5, 3)
_SLA = {"P0": 4, "P1": 24, "P2": 48}


def _hand_for_category(category: str, rng: random.Random) -> str:
    weights = _HAND_WEIGHTS.get(category, _HAND_WEIGHTS["default"])
    hands, w = zip(*weights)
    return rng.choices(list(hands), weights=list(w), k=1)[0]


def _stable_rng(seed: str) -> random.Random:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def generate_tickets(count: int = 1000) -> list[dict[str, Any]]:
    per_category = count // len(USE_CASE_CATEGORIES)
    remainder = count % len(USE_CASE_CATEGORIES)
    rows: list[dict[str, Any]] = []
    seq = 0

    for cat_idx, category in enumerate(USE_CASE_CATEGORIES):
        n_cat = per_category + (1 if cat_idx < remainder else 0)
        templates = _TEMPLATES[category]
        for i in range(n_cat):
            seq += 1
            ticket_id = f"syn-{seq:04d}"
            rng = _stable_rng(ticket_id)
            hand = _hand_for_category(category, rng)
            pool = templates.get(hand) or templates.get("2") or templates.get("3") or []
            title_tpl, desc_tpl, steps = rng.choice(pool)
            n = rng.randint(2, 9)
            title = title_tpl.format(n=n)
            description = desc_tpl.format(n=n)
            priority = rng.choices(_PRIORITY_WEIGHTS, weights=_PRIORITY_W, k=1)[0]
            department = department_for_category(category)
            rows.append(
                {
                    "id": ticket_id,
                    "title": title,
                    "description": description,
                    "category": category,
                    "hand": hand,
                    "department": department,
                    "priority": priority,
                    "sla_hours": _SLA[priority],
                    "urgency": {"P0": "high", "P1": "medium", "P2": "low"}[priority],
                    "resolution_steps": steps,
                    "citations": [f"SYN-{seq:04d}", f"KB-{category[:3].upper()}-{hand}"],
                }
            )
    return rows


def write_corpus(path: Path | None = None, count: int = 1000) -> Path:
    out = path or DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "count": count,
        "description": "Synthetic enterprise tickets for RAG (Use Case 1)",
        "tickets": generate_tickets(count),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = write_corpus()
    print(f"Wrote {p}")
