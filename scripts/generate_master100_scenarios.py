#!/usr/bin/env python3
"""
Generate data/set_master100_scenarios.json — 100 human-written-style IT tickets
for Nextera Technologies (single global technology firm).

Each case has per-ticket gold labels (hand, department, category, acceptable_hands).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "set_master100_scenarios.json"

FIRM = "Nextera Technologies"


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


# 100 scenarios — clear titles, realistic employee language
SCENARIOS: list[Scenario] = [
    # ── Access Management (01–10) ──────────────────────────────────────────
    Scenario(
        "Forgot password — cannot sign in to employee portal",
        "I forgot my Nextera employee portal password and my account is locked after too many attempts. I need to reset it before my 9 AM standup.",
        "1", "Access Management", "Access Management", _h("1"), "medium",
    ),
    Scenario(
        "Authenticator app lost — need MFA reset for VPN",
        "I replaced my phone and lost the Microsoft Authenticator app. I cannot complete MFA when connecting to corporate VPN.",
        "2", "Access Management", "Access Management", _h("1"), "high",
    ),
    Scenario(
        "New hire cannot log in — AD account not provisioned",
        "New hire starting today cannot log in to laptop or email. HR says onboarding is complete but Active Directory account shows not found.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    Scenario(
        "Okta SSO redirect loop on benefits portal",
        "After changing my password yesterday, Okta keeps redirecting in a loop when I open the employee benefits portal. Browser cache cleared, still failing.",
        "2", "Access Management", "Access Management", _h("1"), "medium",
    ),
    Scenario(
        "Employee badge denied at office entry gate",
        "My employee badge shows access denied at the Bangalore office entry gate. HR portal shows badge active but the reader keeps flashing red.",
        "2", "Access Management", "Access Management", _h("2"), "medium",
    ),
    Scenario(
        "Returned from parental leave — need VPN access re-enabled",
        "I returned from parental leave today. I cannot connect to corporate VPN — the client says my remote access account is disabled.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    Scenario(
        "Password expired — self-service reset page errors out",
        "Windows says my password expired. The self-service reset page loads but throws an error after I submit the form.",
        "1", "Access Management", "Access Management", _h("1"), "medium",
    ),
    Scenario(
        "SAP production user locked — need account unlock",
        "SAP GUI shows my production user ID is locked after too many login attempts. I need unlock for month-end journal entries due today.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    Scenario(
        "Contractor access expired — need 30-day extension",
        "My contractor badge and VPN access expired yesterday but the integration project continues two more weeks. Need access extension approved.",
        "2", "Access Management", "Access Management", _h("2"), "medium",
    ),
    Scenario(
        "Privileged access request — Jenkins admin role",
        "I need temporary Jenkins admin role for production hotfix deployment tonight. Manager approved via email.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    # ── Application — collaboration (11–20) ────────────────────────────────
    Scenario(
        "Outlook not syncing new emails since morning",
        "Outlook desktop stopped receiving new emails around 8 AM. Webmail works fine. Send/receive shows no errors.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Microsoft Teams crashes immediately on launch",
        "Teams closes right after splash screen on Windows 11. Error code 0xc0000142. I have customer calls all afternoon.",
        "2", "Application", "Application", _h("1"), "high",
    ),
    Scenario(
        "Zoom app microphone not working in meetings",
        "In Zoom desktop app my microphone shows unmuted but colleagues cannot hear me. Headset works in Spotify and Teams. Zoom version 6.0.4.",
        "1", "Application", "Application", _h("1"), "medium",
    ),
    Scenario(
        "SharePoint finance library permission denied on upload",
        "Cannot upload Q2 forecast spreadsheet to SharePoint finance document library. Error: permission denied. Same folder worked last week.",
        "2", "Access Management", "Access Management", _h("2"), "medium",
    ),
    Scenario(
        "Jira login page blank after Chrome update",
        "Jira Cloud shows a blank white page after yesterday's Chrome update. Tried incognito, same issue.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "Confluence pages timing out for entire team",
        "Our squad Confluence space times out on every page load since 11 AM. Other teams report normal access.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Slack desktop notifications stopped appearing",
        "Slack is open but I no longer get desktop notifications for mentions. Mobile app still alerts normally.",
        "1", "Application", "Application", _h("1"), "low",
    ),
    Scenario(
        "Webex cloud recording missing from last town hall",
        "Webex recording for yesterday's all-hands is not in the portal. Organizer says recording was enabled.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "Google Calendar not showing shared conference rooms",
        "Shared conference room calendars disappeared from Google Calendar sidebar. Cannot book rooms for client workshops.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "OneDrive sync stuck at 99 percent for engineering folder",
        "OneDrive sync icon stuck at 99 percent on the engineering shared folder. Colleagues see my files as outdated. OneDrive for Business client 24.002.",
        "2", "Application", "Application", ["2"], "medium",
    ),
    # ── Application — business systems (21–30) ───────────────────────────
    Scenario(
        "Salesforce opportunity page throws unknown error",
        "Opening any opportunity record in Salesforce shows 'An unexpected error occurred'. Reports and list views work.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Workday timecard submit button spins forever",
        "Workday time entry page spins when I click Submit. Payroll cutoff is tonight for US employees.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "ServiceNow catalog laptop request greyed out",
        "Laptop refresh item in ServiceNow service catalog is greyed out for my location. Policy says I am eligible.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "SAP Fiori finance tile missing after role change",
        "After internal transfer my SAP Fiori finance approval tile is missing. HR confirmed role update in SAP.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Internal HR portal returns 500 error on login",
        "Nextera HR self-service portal returns HTTP 500 immediately after login. Issue started after weekend maintenance.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Expense report stuck in manager pending for two weeks",
        "Concur expense report has been in manager pending for 14 days. Manager says they never received notification.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "CRM customer export produces empty CSV file",
        "Exporting active customer list from internal CRM downloads a 0-byte CSV. Filter shows 12,000 records on screen.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "Revenue billing dashboard spinner for EMEA region only",
        "Revenue billing dashboard in internal BI app shows spinner indefinitely for EMEA users. US team can access the same dashboard normally.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "License portal shows wrong seat count for Figma",
        "Figma license portal shows 45 seats used but we only have 30 designers. Cannot assign new licenses.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "Release portal pipeline queue frozen since midnight",
        "Internal release portal shows all production pipelines queued since 12:05 AM. No deployments have started.",
        "2", "Application", "Application", _h("2"), "critical",
    ),
    # ── Database (31–40) ───────────────────────────────────────────────────
    Scenario(
        "PostgreSQL read replica lag exceeding 20 minutes",
        "Monitoring alert: PostgreSQL read replica lag on orders DB exceeds 20 minutes. Checkout service reading stale inventory.",
        "2", "Database", "Database", _h("2"), "critical",
    ),
    Scenario(
        "MySQL connection pool exhausted on reporting API",
        "Reporting API logs show MySQL connection pool exhausted. Dashboard requests timing out for all users.",
        "2", "Database", "Database", _h("2"), "high",
    ),
    Scenario(
        "SQL Server deadlock blocking payroll batch job",
        "Payroll batch job failed with SQL Server deadlock on HRPROD. Rerun attempted twice, same failure.",
        "2", "Database", "Database", _h("2"), "critical",
    ),
    Scenario(
        "Oracle listener not responding on finance DB host",
        "Cannot connect to Oracle finance database. TNS listener on port 1521 not responding since 6 AM.",
        "2", "Database", "Database", _h("2"), "critical",
    ),
    Scenario(
        "MongoDB Atlas queries timing out on catalog service",
        "Product catalog API queries against MongoDB Atlas M40 timing out. p95 latency jumped from 40ms to 8 seconds.",
        "2", "Database", "Database", _h("2"), "high",
    ),
    Scenario(
        "Redis cluster failover did not complete",
        "Redis cluster primary failed over but new primary not accepting writes. Session cache errors across web tier.",
        "2", "Database", "Database", _h("2"), "critical",
    ),
    Scenario(
        "Snowflake warehouse suspended — overnight ETL blocked",
        "Snowflake virtual warehouse auto-suspended and overnight ETL jobs did not restart. Marketing attribution data stale.",
        "2", "Database", "Database", _h("2"), "high",
    ),
    Scenario(
        "Elasticsearch cluster index status red",
        "Elasticsearch production cluster shows red index status on customer-events index. Kibana searches failing.",
        "2", "Database", "Database", _h("2"), "high",
    ),
    Scenario(
        "DynamoDB throttling on production user-preferences table",
        "DynamoDB ProvisionedThroughputExceededException on user-preferences table during peak login window.",
        "2", "Database", "Database", _h("2"), "high",
    ),
    Scenario(
        "Nightly database backup job failed with checksum error",
        "Last night's full backup of customer DB failed with checksum mismatch. Backup team needs investigation before tonight's run.",
        "2", "Storage", "Storage", _h("2"), "high",
    ),
    # ── Network (41–50) ────────────────────────────────────────────────────
    Scenario(
        "VPN error 619 when connecting from hotel Wi-Fi",
        "GlobalProtect VPN fails with error 619 from hotel Wi-Fi. Need access for executive review deck due tonight.",
        "2", "Network", "Network", _h("1"), "high",
    ),
    Scenario(
        "Internal app DNS name not resolving on corporate network",
        "Hostname inventory.nextera.internal does not resolve on wired network. Was working Friday. nslookup returns NXDOMAIN.",
        "2", "Network", "Network", _h("2"), "high",
    ),
    Scenario(
        "Corporate proxy blocking npm package downloads",
        "npm install fails behind corporate proxy with 403 forbidden for registry.npmjs.org. Blocks frontend build pipeline locally.",
        "2", "Network", "Network", _h("2"), "medium",
    ),
    Scenario(
        "Firewall change blocked SFTP to vendor file drop",
        "After firewall rule push last night SFTP to vendor file drop (sftp.partner.com) times out. Finance cannot send daily settlement files.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "Office Wi-Fi 802.1X certificate expired — Building B",
        "Building B office Wi-Fi rejects connections with certificate expired error. Hundreds of engineers on guest network only.",
        "2", "Network", "Network", _h("2"), "high",
    ),
    Scenario(
        "MPLS link down between Hyderabad and Singapore offices",
        "MPLS circuit between Hyderabad and Singapore shows down since 4 AM. Cross-region file shares unreachable.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "WAN latency spike to primary data center",
        "Network monitoring shows sustained 400ms latency on WAN link to primary data center. Internal apps sluggish for US East users.",
        "2", "Network", "Network", _h("2"), "high",
    ),
    Scenario(
        "Load balancer health checks failing for API gateway",
        "F5 load balancer marks all API gateway pool members down. External health endpoint returns 502.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "IP address conflict on engineering VLAN",
        "Engineering VLAN reports duplicate IP conflict for 10.42.18.44. Several developers lose network intermittently.",
        "2", "Network", "Network", _h("2"), "medium",
    ),
    Scenario(
        "BGP session flapping on internet edge router",
        "BGP session to ISP flapping on edge router ASR-01. Brief internet outages every few minutes for HQ users.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    # ── Infrastructure (51–60) ─────────────────────────────────────────────
    Scenario(
        "Printer paper jam on 5th floor — payroll forms",
        "HP LaserJet on 5th floor shows paper jam. Cannot print signed payroll adjustment forms needed by noon.",
        "1", "Infrastructure", "Infrastructure", _h("1"), "medium",
    ),
    Scenario(
        "Laptop blue screen after Windows update",
        "Company laptop BSOD with stop code PAGE_FAULT_IN_NONPAGED_AREA after Tuesday Windows update. Cannot boot to desktop.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "Conference room projector shows no signal",
        "Projector in Conference Room 12A shows no signal from HDMI laptop input. Tried two cables and two laptops.",
        "1", "Infrastructure", "Infrastructure", _h("1"), "medium",
    ),
    Scenario(
        "VMware host CPU alarm at 98 percent sustained",
        "vCenter alarm: ESXi host esx-prod-07 CPU at 98 percent for 45 minutes. VMs on host running slow.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "Windows file server disk 98 percent full on engineering share",
        "\\\\fileserver\\engineering share reports disk 98 percent full. Team cannot save build artifacts or logs.",
        "2", "Storage", "Storage", _h("2"), "high",
    ),
    Scenario(
        "MacBook FileVault recovery key needed after reboot",
        "MacBook prompted for FileVault recovery key after unexpected reboot. User does not have escrowed key handy.",
        "2", "Application", "Application", _h("2"), "medium",
    ),
    Scenario(
        "Docking station not detecting second monitor",
        "Dell docking station does not detect second monitor after laptop sleep. Unplug-replug works briefly then fails.",
        "1", "Infrastructure", "Infrastructure", _h("1"), "low",
    ),
    Scenario(
        "KVM switch not switching between lab servers",
        "KVM in lab rack stuck on server 2 input. Keyboard and monitor do not switch to server 1 for maintenance.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "medium",
    ),
    Scenario(
        "UPS battery replacement alert in server room 3B",
        "APC UPS in server room 3B reports battery replace required. Runtime estimate below 5 minutes on outage.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "Datacenter rack thermal alert — inlet temperature high",
        "DCIM alert: rack A14 inlet temperature 32°C exceeding threshold. Affected hosts may throttle.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "critical",
    ),
    # ── Storage (61–70) ────────────────────────────────────────────────────
    Scenario(
        "Finance NAS share offline — cannot open spreadsheets",
        "\\\\nas-finance\\shared is offline since 7 AM. Finance team cannot open month-end models.",
        "2", "Storage", "Storage", _h("2"), "critical",
    ),
    Scenario(
        "SAN LUN mapping wrong after storage migration",
        "After weekend SAN migration database server sees incorrect LUN size. SQL Server will not start.",
        "2", "Storage", "Storage", _h("2"), "critical",
    ),
    Scenario(
        "Backup tape library door open alert",
        "Backup system reports tape library door open sensor triggered. Nightly mainframe backup did not start.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "S3 lifecycle policy deleted wrong prefix by mistake",
        "Ops engineer accidentally deleted S3 lifecycle policy for analytics/raw prefix. Compliance wants confirmation no data loss.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Need file restore from Friday backup — deleted folder",
        "User deleted project folder on shared drive yesterday. Need restore from Friday night backup to original path.",
        "2", "Storage", "Storage", _h("2"), "medium",
    ),
    Scenario(
        "NetApp snapshot restore request for legal hold",
        "Legal team requests restore of NetApp snapshot from March 3 for litigation hold. Snapshot exists per storage admin.",
        "2", "Storage", "Storage", _h("2"), "high",
    ),
    Scenario(
        "Azure blob container access denied after policy change",
        "Application cannot read Azure blob container nextera-prod-assets after IAM policy update. 403 on all objects.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    Scenario(
        "iSCSI path down on database server DB-PROD-02",
        "iSCSI paths to storage array show degraded on DB-PROD-02. Multipath reports single path only.",
        "2", "Database", "Database", _h("2"), "critical",
    ),
    Scenario(
        "Archive retrieval slower than 24-hour SLA",
        "Glacier archive retrieval for audit logs has been in progress 36 hours. SLA is 24 hours.",
        "2", "Storage", "Storage", _h("2"), "medium",
    ),
    Scenario(
        "Dropbox Business team folder over quota",
        "Marketing Dropbox Business team folder exceeded quota. Designers cannot upload campaign assets.",
        "2", "Storage", "Storage", _h("2"), "medium",
    ),
    # ── Cloud & developer tools (71–80) ────────────────────────────────────
    Scenario(
        "AWS EC2 production API instance unreachable",
        "Production API EC2 instance i-0a9f2c passes status checks but SSH and HTTPS timeout since deploy.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "GKE cluster nodes NotReady after node pool upgrade",
        "GKE prod cluster node pool upgrade left 3 nodes in NotReady state. Pods stuck pending.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "critical",
    ),
    Scenario(
        "Azure AD app registration certificate expired",
        "Internal SSO integration failing because Azure AD app registration cert expired at midnight. Login errors for partner portal.",
        "2", "Application", "Application", _h("2"), "critical",
    ),
    Scenario(
        "GitHub Actions self-hosted runner offline",
        "Self-hosted GitHub Actions runner nextera-build-05 shows offline. Release pipeline blocked for three repos.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "Docker registry pull rate limited in CI",
        "CI pipelines failing with Docker Hub rate limit exceeded when pulling base images. Affects all feature branches.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "medium",
    ),
    Scenario(
        "Kubernetes pod CrashLoopBackOff on payment service",
        "payment-service pods in prod namespace CrashLoopBackOff after config map update. Customers cannot checkout.",
        "2", "Application", "Application", _h("2"), "critical",
    ),
    Scenario(
        "Terraform state lock stuck after interrupted apply",
        "Terraform apply was interrupted and state lock on S3 backend not released. Team cannot deploy infrastructure changes.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Jenkins build agent disconnected from controller",
        "Jenkins agent label docker-large disconnected. All Docker builds queued with no available executor.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "Artifactory 403 forbidden on Maven dependencies",
        "Maven builds fail pulling dependencies from Artifactory with 403 forbidden. Started after permission audit.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "CloudWatch alarms not firing for RDS CPU",
        "RDS CPU above 90 percent for 20 minutes but CloudWatch alarm did not fire. On-call was not paged.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    # ── Security incidents (81–90) ─────────────────────────────────────────
    Scenario(
        "Security incident: employee clicked phishing link",
        "Employee reported clicking link in phishing email pretending to be IT password reset. Browser forwarded to unknown site.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: ransomware alert on finance laptop",
        "Microsoft Defender flagged ransomware behavior on finance analyst laptop. Machine isolated automatically.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: API key posted in public Slack channel",
        "Engineer accidentally pasted production API key in public Slack channel. Key needs immediate rotation.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: impossible travel login alert",
        "Identity alert: same user logged in from Austin and Singapore within 10 minutes. Possible account compromise.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: USB malware insertion detected",
        "Endpoint protection alert: suspected malware introduced via USB on lab workstation. Device quarantined.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: DDoS attack on customer portal",
        "Security incident: DDoS attack saturating bandwidth to customer portal. WAF triggered but site intermittently down.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: privilege escalation attempt on Linux host",
        "SIEM alert: repeated sudo privilege escalation attempts on production Linux host from unknown IP.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: customer database backup exposed publicly",
        "Security researcher reported publicly accessible S3 object containing customer database backup export.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: compromised service account in GCP",
        "GCP security command center flagged suspicious API calls from service account sa-deploy-prod. Possible key compromise.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    Scenario(
        "Security incident: suspicious outbound traffic to unknown IP",
        "Firewall alert: app server sending sustained outbound traffic to unknown IP in Eastern Europe. Possible C2 beacon.",
        "3", "SecOps", "Security", _h("3"), "critical",
    ),
    # ── Production & cross-cutting (91–100) ────────────────────────────────
    Scenario(
        "Production customer API returning HTTP 503 errors",
        "Customer-facing API returning 503 Service Unavailable since 10:15 AM. Status page not yet updated.",
        "2", "Application", "Application", _h("2"), "critical",
    ),
    Scenario(
        "Payment gateway integration timeout at checkout",
        "Checkout flow times out calling payment gateway integration. Orders stuck in payment pending state.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "LDAP sync broken for customer support portal",
        "Customer support portal LDAP sync job failed overnight. Agents cannot log in with corporate credentials.",
        "2", "Access Management", "Access Management", _h("2"), "high",
    ),
    Scenario(
        "TLS certificate expired on customer portal — browser warning",
        "Browser shows certificate expired warning on portal.nextera.com. Customers reporting they cannot access their accounts.",
        "2", "Network", "Network", _h("2"), "critical",
    ),
    Scenario(
        "Central log aggregation pipeline stopped ingesting EU logs",
        "Splunk forwarders stopped ingesting logs from EU region since 3 AM. Operations dashboards missing events.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
    Scenario(
        "CI build failing on internal Git certificate trust error",
        "All main-branch CI builds fail cloning internal Git with x509 certificate signed by unknown authority.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Mobile app push notifications not delivered",
        "iOS and Android users report no push notifications since app release 4.2.1 yesterday evening.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "GDPR data export tool errors for customer request",
        "GDPR data export tool returns error when processing customer deletion request. Legal deadline in 48 hours.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Monitoring dashboard green but internal apps degraded",
        "Status dashboard shows all green but internal teams report widespread slowness. Possible monitoring blind spot.",
        "2", "Application", "Application", _h("2"), "high",
    ),
    Scenario(
        "Datacenter generator monthly test failed",
        "Scheduled monthly generator test failed to start at primary datacenter. Facilities ticket raised, need IT impact assessment.",
        "2", "Infrastructure", "Infrastructure", _h("2"), "high",
    ),
]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    for i, sc in enumerate(SCENARIOS, 1):
        cases.append(
            {
                "id": f"NX{i:03d}",
                "firm": FIRM,
                "title": sc.title,
                "description": sc.description,
                "urgency": sc.urgency,
                "expect": {
                    "hand": sc.hand,
                    "department": sc.department,
                    "category": sc.category,
                },
                "acceptable_hands": sc.acceptable_hands,
                "notes": f"{FIRM} · {sc.department}",
            }
        )
    return cases


def main() -> int:
    cases = build_cases()
    assert len(cases) == 100, f"expected 100 cases, got {len(cases)}"
    payload = {
        "version": 1,
        "description": (
            "Master100 — 100 human-style IT tickets for Nextera Technologies (global technology firm). "
            "Gold labels per ticket. Primary Nasscom jury validation suite."
        ),
        "firm": FIRM,
        "cases": cases,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
