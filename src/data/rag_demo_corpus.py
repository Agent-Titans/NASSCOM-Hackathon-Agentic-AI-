"""
RAG demo corpus — 45 sample tickets (15 per Hand) for ChromaDB + keyword retrieval.

Each entry: (id, title, description, category, hand, steps, citations)
"""
from __future__ import annotations

from typing import List, Tuple

# (id, title, description, category, hand, steps, citations)
RagDemoEntry = Tuple[str, str, str, str, str, List[str], List[str]]

_HAND1: list[RagDemoEntry] = [
    (
        "rag-h1-01",
        "Forgot portal password",
        "I forgot my password and cannot login to the company portal. Windows login password reset "
        "for active directory account. Locked out and need the link to reset corporate password. "
        "MFA prompt keeps failing after reset.",
        "Access Management",
        "1",
        [
            "Open the company password portal.",
            "Choose Forgot password and verify your identity.",
            "Follow the email link to set a new password (12+ characters).",
            "Sign in again; if MFA fails, contact Identity from this ticket.",
        ],
        ["KB-ACCESS-001", "RAG-H1-01"],
    ),
    (
        "rag-h1-02",
        "Locked out after password change",
        "Cannot login to my account — locked out after password change. Need access restored.",
        "Access Management",
        "1",
        [
            "Confirm the account is not disabled in the identity admin console.",
            "Trigger a fresh password reset from the self-service portal.",
            "Clear browser saved passwords and retry login in a private window.",
            "Re-enroll MFA if the device was replaced during the lockout.",
        ],
        ["KB-ACCESS-002", "RAG-H1-02"],
    ),
    (
        "rag-h1-03",
        "MFA not working on login",
        "MFA locked out — authenticator app codes not working when I try to sign in.",
        "Access Management",
        "1",
        [
            "Verify the device time is synced automatically.",
            "Use a backup MFA method or one-time recovery code if available.",
            "Remove and re-add the authenticator enrollment for the account.",
            "Contact Identity if codes still fail after re-enrollment.",
        ],
        ["KB-ACCESS-003", "RAG-H1-03"],
    ),
    (
        "rag-h1-04",
        "VPN will not connect",
        "Cannot connect to VPN — getting Error 807 when I try to start VPN. Wi-Fi works but VPN client fails to authenticate.",
        "Network",
        "1",
        [
            "Restart VPN client and re-authenticate.",
            "Forget and rejoin Wi-Fi using corporate credentials.",
            "Run built-in network diagnostics and note error codes.",
        ],
        ["KB-NET-007", "RAG-H1-04"],
    ),
    (
        "rag-h1-05",
        "Wi-Fi connected no internet",
        "Corporate Wi-Fi connects but no internet access. DNS seems broken on my laptop.",
        "Network",
        "1",
        [
            "Flush DNS cache and renew DHCP lease on the device.",
            "Switch to an alternate corporate DNS server from the internal KB.",
            "Test with ethernet to isolate Wi-Fi vs DNS issues.",
        ],
        ["KB-NET-008", "RAG-H1-05"],
    ),
    (
        "rag-h1-06",
        "Network connection dropped",
        "Network connection keeps dropping during video calls. Cannot connect to internal apps remotely.",
        "Network",
        "1",
        [
            "Update VPN and Wi-Fi drivers to the approved corporate versions.",
            "Disable power-saving on the network adapter.",
            "Collect VPN client logs and retry from a stable network.",
        ],
        ["KB-NET-009", "RAG-H1-06"],
    ),
    (
        "rag-h1-07",
        "Printer paper jam",
        "Printer on floor 3 has a paper jam — print jobs stuck in queue. Toner level looks OK.",
        "Infrastructure",
        "1",
        [
            "Confirm the printer is online and has paper/toner.",
            "Remove jammed paper following the panel guide.",
            "Reinstall the driver from the internal software catalog.",
        ],
        ["KB-HW-014", "RAG-H1-07"],
    ),
    (
        "rag-h1-08",
        "Printer not printing",
        "Hardware printer not printing — shows offline. Need to print reports today.",
        "Infrastructure",
        "1",
        [
            "Power-cycle the printer and clear the local print spooler.",
            "Set the correct default printer in system settings.",
            "Re-add the printer from the corporate print server.",
        ],
        ["KB-HW-015", "RAG-H1-08"],
    ),
    (
        "rag-h1-09",
        "Excel keeps crashing",
        "Excel application crash every time I open a macro-enabled workbook. Software bug after last update.",
        "Application",
        "1",
        [
            "Confirm the application version and recent updates.",
            "Clear cache and restart the application.",
            "Reinstall from the internal software catalog if crashes persist.",
        ],
        ["KB-APP-020", "RAG-H1-09"],
    ),
    (
        "rag-h1-10",
        "App install failing",
        "Cannot install update for internal CRM app — install fails at 90%. Need software catalog reinstall steps.",
        "Application",
        "1",
        [
            "Remove the partial install using the software center cleanup tool.",
            "Download a fresh package from the internal software catalog.",
            "Reboot and reinstall with admin elevation if prompted.",
        ],
        ["KB-APP-021", "RAG-H1-10"],
    ),
    (
        "rag-h1-11",
        "Database query very slow",
        "Database query slow on reporting DB — SQL report takes 20 minutes. Possible deadlock during month-end.",
        "Database",
        "1",
        [
            "Identify long-running queries on the affected database.",
            "Check replication lag and blocking sessions.",
            "Apply standard DBA runbook for query tuning or failover.",
        ],
        ["KB-DB-011", "RAG-H1-11"],
    ),
    (
        "rag-h1-12",
        "Replication lag on prod DB",
        "SQL replication lag on production database — dashboards stale. Need DBA runbook steps.",
        "Database",
        "1",
        [
            "Check replication agent status and last sync timestamp.",
            "Review blocking transactions on the publisher.",
            "Follow DBA failover/lag remediation runbook if lag exceeds SLA.",
        ],
        ["KB-DB-012", "RAG-H1-12"],
    ),
    (
        "rag-h1-13",
        "Backup job failed",
        "Storage backup failed last night — NAS share quota may be full. Disk archive job error.",
        "Storage",
        "1",
        [
            "Verify storage capacity and quota on the affected share.",
            "Clear stale files or expand quota per policy.",
            "Retry backup job after confirming NAS connectivity.",
        ],
        ["KB-STORAGE-009", "RAG-H1-13"],
    ),
    (
        "rag-h1-14",
        "Share quota exceeded",
        "Cannot save files to network share — storage quota exceeded on team drive.",
        "Storage",
        "1",
        [
            "Review folder usage and archive files older than retention policy.",
            "Request quota increase if still within entitlement limits.",
            "Retry save after space is freed or quota is raised.",
        ],
        ["KB-STORAGE-010", "RAG-H1-14"],
    ),
    (
        "rag-h1-15",
        "Password reset email missing",
        "Forgot password flow — reset email never arrived. Cannot login to SSO portal.",
        "Access Management",
        "1",
        [
            "Check spam/quarantine for messages from the identity mailer.",
            "Confirm the registered email address in the directory.",
            "Resend reset link and verify SMTP logs with Identity if still missing.",
        ],
        ["KB-ACCESS-004", "RAG-H1-15"],
    ),
]

_HAND2: list[RagDemoEntry] = [
    (
        "rag-h2-01",
        "Page not found 401 error",
        "I am unable to access this page — getting page not found and 401 unauthorized in browser.",
        "Application",
        "2",
        [
            "Collect the full URL, timestamp, and screenshot of the 401/page-not-found response.",
            "Confirm the user session is valid — log out and back in.",
            "Clear browser cache or test in a private window and alternate browser.",
            "Verify app health dashboards and recent deployments with Software team.",
        ],
        ["KB-APP-HTTP-401", "RAG-H2-01"],
    ),
    (
        "rag-h2-02",
        "Internal wiki 403 forbidden",
        "HR wiki returns 403 forbidden for my account. I could access it last week.",
        "Application",
        "2",
        [
            "Verify group membership for the wiki space in the access management tool.",
            "Compare with a known-good user on the same team.",
            "Request permission restore or reprovision SSO app assignment.",
        ],
        ["KB-APP-403", "RAG-H2-02"],
    ),
    (
        "rag-h2-03",
        "SSO redirect loop",
        "SSO login redirect loop on benefits portal — never lands on homepage.",
        "Access Management",
        "2",
        [
            "Capture HAR trace during the redirect loop.",
            "Validate SAML/OIDC callback URLs and clock skew on the device.",
            "Coordinate with Identity to refresh federation metadata if needed.",
        ],
        ["KB-ACCESS-SSO", "RAG-H2-03"],
    ),
    (
        "rag-h2-04",
        "API timeout in staging",
        "Staging API returns timeout after 30s when submitting expense form. No clear error code.",
        "Application",
        "2",
        [
            "Reproduce with request ID and payload in staging logs.",
            "Check upstream dependency latency and connection pool limits.",
            "Escalate to app owner if timeout persists after cache warm-up.",
        ],
        ["KB-APP-API", "RAG-H2-04"],
    ),
    (
        "rag-h2-05",
        "Mobile app sync issue",
        "Mobile app not syncing approvals since yesterday. Desktop web works fine.",
        "Application",
        "2",
        [
            "Confirm app version against minimum supported release.",
            "Force logout, clear app cache, and re-authenticate.",
            "Review mobile push/sync service status with Software team.",
        ],
        ["KB-APP-MOBILE", "RAG-H2-05"],
    ),
    (
        "rag-h2-06",
        "Report export corrupt",
        "Exported CSV from analytics tool opens with garbled characters. Excel import fails.",
        "Application",
        "2",
        [
            "Re-export using UTF-8 encoding option if available.",
            "Open with approved import template from the software catalog.",
            "Log defect if corruption reproduces on multiple machines.",
        ],
        ["KB-APP-EXPORT", "RAG-H2-06"],
    ),
    (
        "rag-h2-07",
        "Calendar not syncing",
        "Outlook calendar not syncing meetings from room booking system.",
        "Application",
        "2",
        [
            "Remove and re-add the calendar connector profile.",
            "Verify Exchange/Graph permissions for the mailbox.",
            "Check connector service health with Software support.",
        ],
        ["KB-APP-CAL", "RAG-H2-07"],
    ),
    (
        "rag-h2-08",
        "License activation error",
        "Adobe license activation error on new laptop — serial accepted but app stays in trial mode.",
        "Application",
        "2",
        [
            "Confirm license assignment in the enterprise portal.",
            "Sign out of Creative Cloud and sign in with corporate SSO.",
            "Open ticket with vendor portal if seat count is correct but activation fails.",
        ],
        ["KB-APP-LIC", "RAG-H2-08"],
    ),
    (
        "rag-h2-09",
        "VPN slow not disconnected",
        "VPN connects but internal apps very slow — not a full disconnect, just high latency.",
        "Network",
        "2",
        [
            "Run traceroute over VPN to the affected application subnet.",
            "Switch VPN egress region if split-tunnel policy allows.",
            "Engage Network team if latency exceeds baseline on multiple users.",
        ],
        ["KB-NET-LATENCY", "RAG-H2-09"],
    ),
    (
        "rag-h2-10",
        "Intermittent Wi-Fi drop",
        "Wi-Fi drops only in conference room B — other floors fine. Connection comes back after 2 min.",
        "Network",
        "2",
        [
            "Identify AP name and signal strength in the affected room.",
            "Check recent WLAN controller changes for that floor.",
            "Schedule site survey if drops reproduce on multiple devices.",
        ],
        ["KB-NET-WIFI", "RAG-H2-10"],
    ),
    (
        "rag-h2-11",
        "Custom dashboard blank",
        "Power BI dashboard blank for finance team — data source shows healthy in admin console.",
        "Application",
        "2",
        [
            "Refresh dataset credentials and manual refresh in the workspace.",
            "Validate gateway connectivity for on-prem sources.",
            "Review recent RLS changes with report owner.",
        ],
        ["KB-APP-BI", "RAG-H2-11"],
    ),
    (
        "rag-h2-12",
        "Batch job partial failure",
        "Nightly ETL batch completed with warnings — 3% of rows skipped, no duplicate key error shown.",
        "Database",
        "2",
        [
            "Inspect batch logs for skipped row reasons and source file checksum.",
            "Re-run failed partitions after fixing upstream schema drift.",
            "Coordinate with DBA if constraint violations appear in staging tables.",
        ],
        ["KB-DB-ETL", "RAG-H2-12"],
    ),
    (
        "rag-h2-13",
        "Whitelist IP for SQL database",
        "I need someone to whitelist my IP so I can reach the SQL database from home. Remote connection blocked by firewall.",
        "Network",
        "2",
        [
            "Collect the user's current public IP and target database hostname.",
            "Verify manager approval for remote database access.",
            "Submit firewall rule change to allow the IP on the database security group.",
            "Confirm connectivity after the rule propagates.",
        ],
        ["KB-NET-WHITELIST", "RAG-H2-13"],
    ),
    (
        "rag-h2-14",
        "File upload size limit",
        "Cannot upload 80MB design file to project tool — unclear if limit or network issue.",
        "Application",
        "2",
        [
            "Confirm application upload limit in admin settings.",
            "Test smaller file to isolate size vs network failure.",
            "Use approved large-file transfer share if over app limit.",
        ],
        ["KB-APP-UPLOAD", "RAG-H2-14"],
    ),
    (
        "rag-h2-15",
        "Chrome extension conflict",
        "Internal web app buttons unclickable after Chrome extension update. Works in Safari.",
        "Application",
        "2",
        [
            "Disable third-party extensions and retest the workflow.",
            "Add site to enterprise extension allow list if internal plugin required.",
            "Document conflicting extension for Software standards team.",
        ],
        ["KB-APP-BROWSER", "RAG-H2-15"],
    ),
]

_HAND3: list[RagDemoEntry] = [
    (
        "rag-h3-01",
        "Possible VPN breach",
        "Possible security breach on VPN — unauthorized access detected from unknown IP overnight.",
        "Security",
        "3",
        [
            "Isolate affected accounts and force password reset.",
            "Preserve VPN and authentication logs for SecOps review.",
            "Open incident channel per security response playbook.",
        ],
        ["KB-SEC-001", "RAG-H3-01"],
    ),
    (
        "rag-h3-02",
        "Phishing email clicked",
        "I clicked a phishing email link — security incident. Account may be compromised.",
        "Security",
        "3",
        [
            "Revoke active sessions for the affected user.",
            "Run endpoint scan and mailbox rule audit.",
            "Complete SecOps phishing intake checklist.",
        ],
        ["KB-SEC-002", "RAG-H3-02"],
    ),
    (
        "rag-h3-03",
        "Malware detected on laptop",
        "Antivirus flagged malware on my laptop. Need SecOps to investigate immediately.",
        "Security",
        "3",
        [
            "Disconnect device from corporate network.",
            "Collect EDR timeline and quarantine artifacts.",
            "Follow malware containment runbook with SecOps.",
        ],
        ["KB-SEC-003", "RAG-H3-03"],
    ),
    (
        "rag-h3-04",
        "Ransomware popup",
        "Ransomware popup on shared PC — files encrypted message on screen.",
        "Security",
        "3",
        [
            "Power off device and isolate from network immediately.",
            "Do not pay ransom — notify SecOps incident commander.",
            "Begin backup integrity check on affected shares.",
        ],
        ["KB-SEC-004", "RAG-H3-04"],
    ),
    (
        "rag-h3-05",
        "Unauthorized admin login",
        "Alert: unauthorized login to admin console from foreign country. Security issue.",
        "Security",
        "3",
        [
            "Disable compromised admin credentials pending review.",
            "Enable enhanced logging on admin consoles.",
            "SecOps to validate geo-impossible travel alerts.",
        ],
        ["KB-SEC-005", "RAG-H3-05"],
    ),
    (
        "rag-h3-06",
        "Data exfiltration concern",
        "Suspect data exfiltration — large download from finance share outside business hours.",
        "Security",
        "3",
        [
            "Preserve DLP and file-share audit logs.",
            "Restrict access to affected dataset pending investigation.",
            "Engage SecOps and legal per data-loss procedure.",
        ],
        ["KB-SEC-006", "RAG-H3-06"],
    ),
    (
        "rag-h3-07",
        "Security certificate expired",
        "Production TLS certificate expired — customers see security warning on portal.",
        "Security",
        "3",
        [
            "Validate cert expiry on load balancers and origin servers.",
            "Deploy renewed cert from approved PKI store.",
            "Confirm external monitor clears after propagation.",
        ],
        ["KB-SEC-007", "RAG-H3-07"],
    ),
    (
        "rag-h3-08",
        "Suspicious USB device",
        "Found unknown USB device inserted in lobby kiosk — possible hack attempt.",
        "Security",
        "3",
        [
            "Remove USB and secure kiosk offline.",
            "Image disk per forensic SOP before reboot.",
            "Review physical access logs with facilities and SecOps.",
        ],
        ["KB-SEC-008", "RAG-H3-08"],
    ),
    (
        "rag-h3-09",
        "Duplicate issues in Data",
        "I am getting duplicate issues from upstream data — quality problem, no error codes.",
        "Database",
        "3",
        [
            "Identify duplicate keys in staging and production tables.",
            "Trace upstream feed for repeated batch submissions.",
            "Apply DBA deduplication runbook after root-cause confirmation.",
        ],
        ["KB-DB-DEDUP", "RAG-H3-09"],
    ),
    (
        "rag-h3-10",
        "Upstream data mismatch",
        "Upstream data mismatch in pipeline — not sure which system owns the issue.",
        "Database",
        "3",
        [
            "Compare record counts and checksums between source and landing zone.",
            "Engage upstream system owner with sample mismatched rows.",
            "Pause downstream consumers until data integrity is restored.",
        ],
        ["KB-DB-MISMATCH", "RAG-H3-10"],
    ),
    (
        "rag-h3-11",
        "Something broken",
        "Something is broken. Please help.",
        "Application",
        "3",
        [
            "Contact requester for device, application, and error details.",
            "Classify once symptoms are confirmed.",
            "Assign to appropriate queue after triage interview.",
        ],
        ["KB-TRIAGE-001", "RAG-H3-11"],
    ),
    (
        "rag-h3-12",
        "IT help needed",
        "Need IT help asap — computer not working. No other details.",
        "Application",
        "3",
        [
            "Schedule live triage with requester.",
            "Gather minimum viable symptoms before routing.",
            "Escalate to specialist if hardware or security indicators appear.",
        ],
        ["KB-TRIAGE-002", "RAG-H3-12"],
    ),
    (
        "rag-h3-13",
        "General access problem",
        "Cannot access stuff for my job. Happened recently.",
        "Access Management",
        "3",
        [
            "Interview user to identify which systems are affected.",
            "Check recent entitlement changes and MFA status.",
            "Route to Identity or app team after scope is defined.",
        ],
        ["KB-TRIAGE-003", "RAG-H3-13"],
    ),
    (
        "rag-h3-14",
        "Weird error on screen",
        "Weird error on screen — did not write it down. Intermittent.",
        "Application",
        "3",
        [
            "Ask for screenshot or photo at next occurrence.",
            "Enable verbose client logging if supported.",
            "Reproduce with specialist on live session if possible.",
        ],
        ["KB-TRIAGE-004", "RAG-H3-14"],
    ),
    (
        "rag-h3-15",
        "VPN access security policy block",
        "Not able to access VPN — may be security policy block after international travel.",
        "Security",
        "3",
        [
            "Verify travel geo-fence policy triggered on account.",
            "Collect user location and device compliance status.",
            "SecOps to approve temporary VPN exception if policy allows.",
        ],
        ["KB-SEC-VPN", "RAG-H3-15"],
    ),
]

RAG_DEMO_CORPUS: list[RagDemoEntry] = _HAND1 + _HAND2 + _HAND3


def corpus_search_document(entry: RagDemoEntry) -> str:
    """Text indexed in ChromaDB and used for keyword overlap."""
    _id, title, description, category, _hand, _steps, _cites = entry
    return f"{title}\n{description}\n{category}"


_CATEGORY_TO_DEPARTMENT: dict[str, str] = {
    "Infrastructure": "Hardware",
    "Application": "Software",
    "Security": "SecOps",
    "Database": "DBA",
    "Storage": "Storage",
    "Network": "Network",
    "Access Management": "Access Management",
}

_DEPARTMENT_TO_ASSIGNEE_EMAIL: dict[str, str] = {
    "Hardware": "sree@employee",
    "Software": "subbu@employee",
    "SecOps": "narsimha@employee",
    "Network": "shashi@employee",
    "Access Management": "satya@employee",
    "DBA": "sagar@employee",
    "Storage": "sagar@employee",
}

_REQUESTER_EMAILS: tuple[str, ...] = (
    "pallavi@user",
    "gajanan@user",
    "imran@user",
    "naveen@user",
    "santhosh@user",
)

_SLA_BY_PRIORITY: dict[str, tuple[int, ...]] = {
    "P0": (4, 8),
    "P1": (12, 24),
    "P2": (24, 48),
}


def department_for_category(category: str) -> str:
    return _CATEGORY_TO_DEPARTMENT.get(category, "Software")


def assignee_email_for_department(department: str) -> str:
    return _DEPARTMENT_TO_ASSIGNEE_EMAIL.get(department, "subbu@employee")


def demo_ticket_routing(doc_id: str, category: str, hand: str) -> dict[str, object]:
    """
  Deterministic per-ticket routing: department from category,
  pseudo-random priority + SLA from ticket id hash.
    """
    import random

    rng = random.Random(hash(doc_id) & 0xFFFFFFFF)
    department = department_for_category(category)
    priority = rng.choices(["P0", "P1", "P2"], weights=[2, 4, 4], k=1)[0]
    sla_hours = int(rng.choice(_SLA_BY_PRIORITY[priority]))
    urgency = {"P0": "high", "P1": "medium", "P2": "low"}[priority]
    requester_email = rng.choice(_REQUESTER_EMAILS)
    assignee_email = assignee_email_for_department(department)
    # Hand 1 self-help corpus tickets usually closed without assignee
    if hand == "1":
        assignee_email = rng.choice([assignee_email, ""])  # 50% historical assignee
    confidence = 0.88 if hand == "1" else 0.72 if hand == "2" else 0.42
    return {
        "department_queue": department,
        "priority": priority,
        "sla_hours": sla_hours,
        "urgency": urgency,
        "requester_email": requester_email,
        "assignee_email": assignee_email,
        "escalation_required": hand == "3" or category == "Security",
        "confidence": confidence,
    }
