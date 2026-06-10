"""KB seed documents indexed alongside RAG demo + enterprise corpus."""
from __future__ import annotations

# (id, search_doc, category, steps, citations)
KbSeedEntry = tuple[str, str, str, list[str], list[str]]

KB_SEED_CORPUS: list[KbSeedEntry] = [
    (
        "kb-access-001",
        "Forgot password cannot login MFA locked out access account Windows login active directory "
        "corporate password reset locked out",
        "Access Management",
        [
            "Open the company password portal.",
            "Choose Forgot password and verify your identity.",
            "Follow the email link to set a new password (12+ characters).",
            "Sign in again; if MFA fails, contact Identity from this ticket.",
        ],
        ["KB-ACCESS-001", "TICKET-1042"],
    ),
    (
        "kb-net-007",
        "VPN wifi network connection dns internet cannot connect",
        "Network",
        [
            "Restart VPN client and re-authenticate.",
            "Forget and rejoin Wi-Fi using corporate credentials.",
            "Run built-in network diagnostics and note error codes.",
        ],
        ["KB-NET-007"],
    ),
    (
        "kb-hw-014",
        "Printer print toner paper jam hardware",
        "Infrastructure",
        [
            "Confirm the printer is online and has paper/toner.",
            "Remove jammed paper following the panel guide.",
            "Reinstall the driver from the internal software catalog.",
        ],
        ["KB-HW-014"],
    ),
    (
        "kb-app-020",
        "Software application crash bug install update excel macro",
        "Application",
        [
            "Confirm the application version and recent updates.",
            "Clear cache and restart the application.",
            "Reinstall from the internal software catalog if crashes persist.",
        ],
        ["KB-APP-020"],
    ),
    (
        "kb-db-011",
        "Database query slow replication sql deadlock report",
        "Database",
        [
            "Identify long-running queries on the affected database.",
            "Check replication lag and blocking sessions.",
            "Apply standard DBA runbook for query tuning or failover.",
        ],
        ["KB-DB-011"],
    ),
    (
        "kb-storage-009",
        "Storage backup disk share quota file nas archive",
        "Storage",
        [
            "Verify storage capacity and quota on the affected share.",
            "Clear stale files or expand quota per policy.",
            "Retry backup job after confirming NAS connectivity.",
        ],
        ["KB-STORAGE-009"],
    ),
]
