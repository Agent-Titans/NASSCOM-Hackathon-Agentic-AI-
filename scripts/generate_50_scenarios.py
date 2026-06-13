#!/usr/bin/env python3
"""Generate data/pallavi_50_scenarios.json — 50 diverse LLD-aligned cases."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "pallavi_50_scenarios.json"

CASES = [
    # Network (8)
    ("N01", "VPN Split Tunnel Not Routing", "Cisco AnyConnect connects but internal subnets 10.20.0.0/16 are unreachable. Split tunnel policy may be misapplied on the VPN gateway.", "low", "Network", "Network", "1", ["1", "2"]),
    ("N02", "Corporate DNS MX Record Failure", "Inbound email bouncing — external DNS MX records for mail.corp.local not resolving. nslookup fails from office network.", "medium", "Network", "Network", "2", ["1", "2"]),
    ("N03", "Firewall Blocking HTTPS Egress", "Outbound HTTPS on port 443 to api.partner.com blocked by perimeter firewall. Need allow rule for integration.", "low", "Network", "Network", "2", ["1", "2"]),
    ("N04", "Guest Wi-Fi Captive Portal Loop", "Guest Wi-Fi connects but captive portal page reloads endlessly. Users cannot complete network authentication.", "low", "Network", "Network", "1", ["1", "2"]),
    ("N05", "Load Balancer Pool Unhealthy", "F5 load balancer marks all nodes in checkout-pool unhealthy. Users see 502 bad gateway at the edge.", "medium", "Network", "Network", "2", ["1", "2"]),
    ("N06", "Zscaler PAC File Misconfiguration", "Zscaler PAC file sending traffic to wrong proxy port. Internal Jenkins agents cannot reach artifact repo.", "medium", "Network", "Network", "2", ["1", "2"]),
    ("N07", "MPLS Circuit Packet Loss", "MPLS WAN link between HQ and DR site showing 8% packet loss. Latency spikes on VoIP and replication traffic.", "medium", "Network", "Network", "2", ["1", "2"]),
    ("N08", "SSL VPN Certificate Trust Error", "VPN client shows untrusted server certificate when connecting remotely. Corporate root CA may have expired on gateway.", "low", "Network", "Network", "1", ["1", "2"]),
    # Infrastructure (8)
    ("I01", "Docking Station Display Not Detected", "Thunderbolt dock powers laptop but external Dell monitor shows no signal. USB-C display path not enumerating.", "low", "Infrastructure", "Hardware", "2", ["1", "2"]),
    ("I02", "Laptop Keyboard Keys Unresponsive", "Several keys on company MacBook Pro keyboard stopped registering input. Physical keyboard hardware failure suspected.", "medium", "Infrastructure", "Hardware", "2", ["1", "2", "3"]),
    ("I03", "Server Rack PDU Tripped", "PDU in rack A3 tripped breaker. Three production servers powered off unexpectedly in datacenter row 4.", "high", "Infrastructure", "Hardware", "2", ["2", "3"]),
    ("I04", "Secure Boot Blocking Driver", "Windows laptop blocks new Wi-Fi driver install — Secure Boot policy prevents unsigned driver load after firmware update.", "medium", "Infrastructure", "Hardware", "2", ["1", "2"]),
    ("I05", "Hyper-V Host CPU Thermal Alert", "Hyper-V host HV-PROD-03 reporting CPU thermal throttling. Virtual machines experiencing performance degradation.", "high", "Infrastructure", "Hardware", "2", ["2", "3"]),
    ("I06", "Fleet Printer Toner Critical", "Floor 5 HP printer fleet reports critical toner on 6 devices. Print queue backing up for finance department.", "low", "Infrastructure", "Hardware", "1", ["1", "2"]),
    ("I07", "Laptop SMART Disk Failure Warning", "Dell laptop BIOS reports SMART disk failure imminent. User cannot boot reliably — hardware replacement needed.", "high", "Infrastructure", "Hardware", "2", ["2", "3"]),
    ("I08", "UPS Battery Replacement Overdue", "UPS in server room B reporting end-of-life battery. Runtime under 3 minutes on simulated power fail test.", "medium", "Infrastructure", "Hardware", "2", ["1", "2", "3"]),
    # Application (8)
    ("A01", "Outlook Calendar Not Syncing", "Microsoft Outlook desktop client stopped syncing calendar events. Web Outlook works but desktop shows stale meetings.", "low", "Application", "Software", "1", ["1", "2"]),
    ("A02", "Chrome Extension Crash Loop", "Internal Chrome extension causes browser crash on launch. Desktop client unusable for procurement portal.", "medium", "Application", "Software", "2", ["1", "2"]),
    ("A03", "Jira Workflow Transition Error", "Jira ticket workflow transition fails with script error when moving from In Review to Done. Application workflow bug.", "low", "Application", "Software", "2", ["1", "2"]),
    ("A04", "Slack Desktop Notifications Silent", "Slack desktop app not showing notifications on Windows 11. Messages arrive but no toast or badge updates.", "low", "Application", "Software", "1", ["1", "2"]),
    ("A05", "Java Runtime Missing for ERP Client", "Internal ERP desktop client fails to launch — Java Runtime Environment not found after workstation image refresh.", "medium", "Application", "Software", "2", ["1", "2"]),
    ("A06", "Mobile Push Notifications Failed", "Corporate mobile app push notifications stopped on iOS devices after certificate rotation. Application backend integration issue.", "medium", "Application", "Software", "2", ["1", "2"]),
    ("A07", "Power BI Dataset Refresh Error", "Power BI scheduled dataset refresh fails with gateway timeout. Report shows stale data in executive dashboard.", "medium", "Application", "Software", "2", ["1", "2"]),
    ("A08", "IDE Build Toolchain Failure", "Visual Studio build fails with MSB4018 task error after NuGet package update. Local development toolchain broken.", "low", "Application", "Software", "2", ["1", "2"]),
    # Security (7)
    ("S01", "Suspicious Login from Foreign IP", "Security incident: multiple failed and one successful login for finance user from IP in unfamiliar country. Suspected account compromise.", "high", "Security", "SecOps", "3", ["3"]),
    ("S02", "USB Malware Scan Positive", "Endpoint protection flagged malware on USB drive inserted into workstation WS-HR-19. Quarantine and forensics required.", "high", "Security", "SecOps", "3", ["2", "3"]),
    ("S03", "Spear Phishing Targeting Executive", "CFO received targeted phishing email with malicious attachment disguised as board report. Security incident — do not open.", "high", "Security", "SecOps", "3", ["3"]),
    ("S04", "DLP Credit Card Data Export Alert", "Data loss prevention alert: user attempted to email file containing credit card numbers to external address.", "high", "Security", "SecOps", "3", ["3"]),
    ("S05", "Compromised Service Account Detected", "Security incident: service account SVC-BILLING shows impossible travel logins. Credential compromise suspected — rotate immediately.", "high", "Security", "SecOps", "3", ["3"]),
    ("S06", "SQL Injection in Web Access Logs", "WAF detected SQL injection attempts against customer portal. Active attack pattern in Apache access logs — investigate source IPs.", "high", "Security", "SecOps", "3", ["3"]),
    ("S07", "Pen Test Critical Finding Open", "External penetration test reported critical finding: unpatched RCE on edge service. Remediation required before audit deadline.", "medium", "Security", "SecOps", "3", ["2", "3"]),
    # Database (7)
    ("D01", "Oracle Tablespace Full", "Oracle database ORCLPROD tablespace USERS at 99% capacity. Inserts failing with ORA-01653 unable to extend table.", "high", "Database", "DBA", "2", ["1", "2"]),
    ("D02", "MySQL Slow Query Spike", "MySQL production instance slow query log shows 500+ queries over 10s. Reporting batch job degrading database performance.", "medium", "Database", "DBA", "2", ["1", "2"]),
    ("D03", "Inventory Deadlock Error", "SQL Server inventory module throwing deadlock error 1205 on stock adjustment transactions during month-end close.", "medium", "Database", "DBA", "2", ["1", "2"]),
    ("D04", "MongoDB Replica Election Failed", "MongoDB replica set member failed election. Secondary cannot sync — replica lag growing on analytics cluster.", "high", "Database", "DBA", "2", ["2", "3"]),
    ("D05", "Failed SQL Migration Rollback", "Production SQL migration script failed mid-run. Need DBA to rollback schema changes and restore consistent state.", "high", "Database", "DBA", "2", ["2", "3"]),
    ("D06", "Reporting DB Connection Pool Timeout", "PostgreSQL reporting database connection pool exhausted. Dashboard queries timeout with too many connections during peak hours.", "medium", "Database", "DBA", "2", ["1", "2"]),
    ("D07", "Index Rebuild Blocking Production", "Nightly index rebuild on ORDERS table blocking production inserts. Database maintenance window overrun.", "medium", "Database", "DBA", "2", ["1", "2"]),
    # Storage (6)
    ("ST01", "NAS Share Out of Space", "File server NAS volume \\\\files\\engineering at 98% capacity. Engineers cannot save CAD files to shared storage.", "medium", "Storage", "DBA", "2", ["1", "2"]),
    ("ST02", "OneDrive Sync Conflict Loop", "OneDrive client stuck in sync conflict loop for shared project folder. Files show red X — storage sync issue not application crash.", "low", "Storage", "DBA", "2", ["1", "2"]),
    ("ST03", "SharePoint Permission Inheritance Broken", "SharePoint HR library lost permission inheritance after site migration. Users see access denied on file share documents.", "low", "Storage", "DBA", "2", ["1", "2"]),
    ("ST04", "Tape Library Robot Arm Jam", "Backup tape library robot arm jammed during weekly full backup. Storage hardware blocking backup media swap.", "medium", "Storage", "DBA", "2", ["2", "3"]),
    ("ST05", "DFS Replication Stopped", "Windows DFS replication for \\\\dfs\\dept shares stopped with error 9098. File server replication backlog growing.", "medium", "Storage", "DBA", "2", ["1", "2"]),
    ("ST06", "Archive Storage Quota Exceeded", "Cold archive storage tier quota exceeded for legal hold bucket. New compliance archives cannot be written.", "low", "Storage", "DBA", "2", ["1", "2"]),
    # Access Management (6)
    ("AM01", "Contractor Access Extension", "Contractor account for temp.vendor expires Friday. Request 30-day extension for Active Directory and VPN access.", "low", "Access Management", "Access Management", "2", ["1", "2"]),
    ("AM02", "Service Account Password Rotation", "Scheduled password rotation for SVC-ETL service account in Active Directory. Standard identity maintenance request.", "low", "Access Management", "Access Management", "2", ["1", "2"]),
    ("AM03", "SSO SAML Assertion Failure", "Users cannot SSO into vendor SaaS app — SAML assertion validation fails at identity provider. Login federation issue.", "medium", "Access Management", "Access Management", "2", ["1", "2"]),
    ("AM04", "Disable Terminated Contractor Account", "Contractor engagement ended today. Please disable AD account and revoke all system access for contractor@vendor.com.", "medium", "Access Management", "Access Management", "2", ["1", "2"]),
    ("AM05", "Create Distribution List Request", "Create new mail-enabled distribution list dl-sales-apac@corp.com for APAC sales team. Manager approval attached.", "low", "Access Management", "Access Management", "2", ["1", "2"]),
    ("AM06", "Break-Glass Admin for Incident", "Incident bridge request: temporary privileged admin access to production AD for sev-1 outage. Standard break-glass workflow.", "high", "Access Management", "Access Management", "2", ["2", "3"]),
]

payload = {
    "version": 1,
    "description": "50 diverse IT scenarios — Set D (LLD-aligned)",
    "cases": [
        {
            "id": cid,
            "title": title,
            "description": desc,
            "urgency": {"low": "low", "medium": "medium", "high": "high"}[urg],
            "expect": {"hand": hand, "department": dept, "category": cat},
            "acceptable_hands": hands,
            "notes": f"{cat} scenario",
        }
        for cid, title, desc, urg, cat, dept, hand, hands in CASES
    ],
}

OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Wrote {len(CASES)} cases to {OUT}")
