#!/usr/bin/env python3
"""Generate data/set_jury100_scenarios.json — 100 office/tech tickets, 4 firms × 25."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "set_jury100_scenarios.json"

# (id_prefix, firm_name, office_label)
FIRMS = (
    ("MS", "Microsoft", "Redmond campus"),
    ("HS", "HSBC Tech", "London technology centre"),
    ("JP", "JPMorgan Tech", "Brooklyn tech hub"),
    ("CG", "Capgemini", "Paris delivery centre"),
)

# 25 tickets per firm: dept distribution
DEPT_PLAN = [
    ("Application", "2", "Application"),
    ("Application", "2", "Application"),
    ("Application", "2", "Application"),
    ("Application", "2", "Application"),
    ("Application", "2", "Application"),
    ("Application", "2", "Application"),
    ("Database", "2", "Database"),
    ("Database", "2", "Database"),
    ("Database", "2", "Database"),
    ("Database", "2", "Database"),
    ("Database", "2", "Database"),
    ("Access Management", "2", "Access Management"),
    ("Access Management", "2", "Access Management"),
    ("Access Management", "2", "Access Management"),
    ("Access Management", "1", "Access Management"),
    ("Access Management", "1", "Access Management"),
    ("Network", "2", "Network"),
    ("Network", "2", "Network"),
    ("Network", "2", "Network"),
    ("Network", "2", "Network"),
    ("Infrastructure", "2", "Infrastructure"),
    ("Infrastructure", "2", "Infrastructure"),
    ("Storage", "2", "Storage"),
    ("SecOps", "3", "Security"),
    ("SecOps", "3", "Security"),
]

TEMPLATES: dict[str, list[tuple[str, str, str]]] = {
    "Microsoft": [
        ("Teams meeting lobby bypass failure", "Microsoft Teams external guest stuck in lobby for executive briefing. Lobby policy change blocked auto-admit for trusted partners."),
        ("SharePoint site collection restore pending", "SharePoint Online site collection accidentally deleted. Admin center shows restore window expiring in 4 hours."),
        ("Azure DevOps pipeline YAML validation error", "Azure DevOps release pipeline fails YAML schema validation after template library upgrade. Production deployment blocked."),
        ("Power BI dataset refresh gateway offline", "On-premises data gateway for Power BI finance dataset offline. Scheduled refresh failed three consecutive runs."),
        ("Dynamics 365 sales entity sync failure", "Dynamics 365 opportunity sync to Dataverse failing with plugin exception. EMEA forecast commit at risk."),
        ("SQL Azure elastic pool DTU exhaustion", "Azure SQL elastic pool DTU pegged at 100 percent. CRM microservice timeouts during business hours."),
        ("Cosmos DB request rate throttling alert", "Cosmos DB container returning 429 throttling on user profile service. Autoscale not keeping up with peak."),
        ("PostgreSQL flexible server failover test failed", "Azure Database for PostgreSQL planned failover test did not complete. Replica lag above 10 minutes."),
        ("Synapse dedicated SQL pool blocking chain", "Synapse dedicated SQL pool blocking chain on marketing mart load. ETL job killed after 2 hour wait."),
        ("Fabric warehouse load job permission denied", "Microsoft Fabric warehouse COPY INTO fails with permission denied on ADLS Gen2 staging path."),
        ("Entra ID conditional access blocks contractor laptop", "Contractor laptop blocked by Entra conditional access policy requiring compliant device. Project onboarding delayed."),
        ("Privileged Identity Management activation stuck", "PIM role activation for Azure subscription owner pending approval 6 hours. Emergency change window closing."),
        ("FIDO2 security key enrollment failure", "Employee FIDO2 key enrollment fails at Windows Hello setup. Smart card middleware conflict suspected."),
        ("Service principal secret expired for Graph API", "Automation service principal client secret expired. Mailbox provisioning runbook failing."),
        ("MFA number matching not received on mobile", "Authenticator push MFA number matching prompt not received on corporate mobile. User locked out of O365."),
        ("ExpressRoute BGP session down primary circuit", "ExpressRoute primary circuit BGP session down between Seattle and Azure region. Failover latency spike."),
        ("VPN split tunnel policy blocking GitHub Copilot", "Corporate VPN split tunnel policy blocks GitHub Copilot endpoints. Developers cannot use approved AI assistant."),
        ("Wi-Fi 6E SSID authentication failure Building 34", "Wi-Fi 6E SSID 802.1X authentication fails for Building 34 engineers. RADIUS timeout to NPS cluster."),
        ("DNS conditional forwarder stale for internal API", "Internal API hostname resolves to decommissioned IP after datacenter migration. Split DNS records stale."),
        ("Hyper-V cluster live migration failure", "Hyper-V cluster live migration fails with insufficient resources on destination node. Patch maintenance blocked."),
        ("Windows Server patch reboot loop on file cluster", "Windows Server cumulative update causes reboot loop on scale-out file server cluster node."),
        ("OneDrive sync client throttling large engineering share", "OneDrive sync client throttling on 50GB engineering share. Desktop shows constant syncing state."),
        ("Azure Files share quota exceeded for dev tools", "Azure Files premium share quota exceeded. Build artifact uploads failing for platform team."),
        ("Security incident: OAuth consent phishing targeting admins", "Security incident: OAuth consent phishing campaign targeting Entra global admins detected. Suspicious enterprise app consent requests logged."),
        ("Security incident: malware on build agent VM", "Security incident: Defender alert for malware on self-hosted Azure DevOps build agent. Agent pool quarantined."),
    ],
    "HSBC Tech": [
        ("Mainframe CICS transaction abend on payments screen", "HSBC payments CICS transaction abends with ASRA on high-value transfer screen. EMEA clearing cut-off in 90 minutes."),
        ("Oracle Flexcube batch job failed overnight", "Oracle Flexcube end-of-day batch aborts on interest accrual step. Downstream regulatory report delayed."),
        ("Temenos Transact API timeout on loan origination", "Temenos Transact REST API timeout during retail loan origination. Branch staff using paper fallback."),
        ("SWIFT Alliance Access message queue backlog", "SWIFT Alliance Access message queue backlog after gateway certificate renewal. Outbound payments queuing."),
        ("Kondor+ risk blotter not loading market data", "Kondor+ risk blotter fails to load real-time FX rates. Traders using stale prices for VAR."),
        ("Db2 HADR standby lag on trade ledger", "Db2 HADR standby lag exceeds 20 minutes on trade ledger database. Failover readiness degraded."),
        ("MongoDB sharded cluster balancer stuck", "MongoDB sharded cluster balancer stuck migrating chunks on customer analytics DB."),
        ("SQL Server Always On availability group not synchronizing", "SQL Server AG secondary not synchronizing after storage firmware upgrade."),
        ("Redis cluster memory eviction on session store", "Redis cluster aggressive eviction on digital banking session store. Mobile logins intermittently fail."),
        ("PostgreSQL logical replication slot inactive", "PostgreSQL logical replication slot inactive on fraud scoring replica. Feature store stale."),
        ("CyberArk safe access request expired", "CyberArk privileged access request for production DB expired before approval. DBA cannot run emergency fix."),
        ("SailPoint identity certification campaign stuck", "SailPoint certification campaign stuck on manager review for 400 trading accounts."),
        ("Smart card PIN unlock for HSM operator", "HSM operator smart card locked after three wrong PIN attempts. Payment signing halted."),
        ("VPN token seed mismatch after phone replacement", "RSA SecurID soft token seed mismatch after phone replacement. Remote trader cannot connect."),
        ("Active Directory privileged group nested membership error", "AD nested group membership not reflecting for SWIFT operator role. Access review failing."),
        ("MPLS link congestion between HK and UK hubs", "MPLS WAN congestion between Hong Kong and UK trading hubs during month-end. Voice turrets degrading."),
        ("Firewall policy blocking FIX session to LP", "Perimeter firewall change blocking FIX 4.4 session to liquidity provider. Equities desk offline."),
        ("Proxy PAC file serving wrong datacenter route", "PAC file serving stale route sending APAC users to EU proxy. Latency above 400ms."),
        ("Load balancer SSL handshake failure on API gateway", "F5 load balancer SSL handshake failures on open banking API gateway after cert chain update."),
        ("Blade server PSU fault in primary trading rack", "HP blade chassis PSU fault in primary London trading rack. Redundancy lost on half chassis."),
        ("VMware vMotion failure on risk calculation cluster", "vMotion fails on risk calculation cluster during host maintenance. Batch VAR run delayed."),
        ("NetApp volume snapshot restore needed for legal hold", "NetApp snapshot restore required for legal hold on archived email PST share."),
        ("SAN fabric zone misconfiguration after switch upgrade", "Brocade SAN zoning misconfiguration after firmware upgrade. DB LUN paths down."),
        ("Security incident: credential stuffing on retail banking portal", "Security incident: credential stuffing attack detected on retail banking login. WAF flagged 12k attempts from botnet."),
        ("Security incident: suspicious PowerShell on trader workstation", "Security incident: EDR flagged suspicious PowerShell download cradle on trader workstation. Host isolated."),
    ],
    "JPMorgan Tech": [
        ("Athena risk report grid timeout", "Athena risk report grid times out loading cross-asset Greeks for US desk. Risk meeting in 1 hour."),
        ("LOLR liquidity dashboard stale positions", "LOLR liquidity dashboard showing stale positions after ETL failure. Treasury using manual spreadsheet."),
        ("Fusion platform API gateway 502 errors", "Fusion platform API gateway returning 502 on client onboarding workflow. API mesh circuit open."),
        ("SimCorp Dimension corporate action import failed", "SimCorp Dimension corporate action import failed validation. Fixed income ops blocked."),
        ("Collibra data catalog lineage broken for trade feed", "Collibra lineage graph broken for trade feed after schema rename. Data governance audit finding."),
        ("Cassandra repair failing on market data keyspace", "Cassandra nodetool repair aborts on market data keyspace. Read consistency warnings."),
        ("Oracle Exadata cell disk offline", "Exadata storage cell disk offline on trade warehouse. Smart scan performance degraded."),
        ("Sybase ASE tempdb full on equities database", "Sybase ASE tempdb full during bulk load on equities database. Batch aborted."),
        ("Snowflake warehouse auto-suspend during month-end", "Snowflake warehouse auto-suspended during month-end regulatory extract. Job queue backed up."),
        ("ElasticSearch cluster red status on log analytics", "ElasticSearch cluster red after unassigned shards on security log index."),
        ("ForgeRock SSO assertion validation failure", "ForgeRock SAML assertion validation failure for internal research portal after IdP cert rollover."),
        ("BeyondTrust session recording not starting", "BeyondTrust privileged session recording not starting for DBA jump box. Compliance audit gap."),
        ("Trading desk badge not provisioning after transfer", "Physical access badge not provisioned after internal desk transfer. Trader cannot enter floor."),
        ("Kerberos SPN duplicate on pricing service account", "Duplicate Kerberos SPN on pricing service account causing authentication failures."),
        ("YubiKey OTP sync drift on rates desk", "YubiKey OTP sync drift blocking VPN login for rates desk analyst."),
        ("Cross-connect latency spike to NYSE matching engine", "Cross-connect latency spike to colo matching engine. Algo orders missing queue position."),
        ("Multicast feed gap on US equity depth channel", "Multicast equity depth feed gap detected on primary channel. Pricing engine using backup."),
        ("BGP route leak from DR site affecting market data VPN", "BGP route leak from DR site injecting prefixes into market data VPN."),
        ("DNSSEC validation failure on internal pricing hostname", "DNSSEC validation failure on internal pricing API hostname after key rollover."),
        ("Trading floor UPS battery test failure", "UPS battery test failure on trading floor power distribution unit. Facilities escalation."),
        ("Linux kernel panic on low-latency pricing server", "Linux kernel panic on low-latency pricing server after NIC driver update."),
        ("Isilon cluster snapshot policy not running", "Isilon snapshot policy missed 3 cycles on research file share. RPO at risk."),
        ("Object storage lifecycle rule deleted research archive", "S3 lifecycle misconfiguration moved research archive to Glacier early. Retrieval delay."),
        ("Security incident: market data API key exposed in chat", "Security incident: production market data API key pasted in Teams channel. Key rotation required."),
        ("Security incident: ransomware probe on file transfer server", "Security incident: ransomware behavior detected on managed file transfer server. Shares isolated."),
    ],
    "Capgemini": [
        ("SAP SuccessFactors performance review workflow stuck", "SuccessFactors performance review workflow stuck in pending step for 200 managers. HR deadline tonight."),
        ("ServiceNow CMDB CI reconciliation job failing", "ServiceNow CMDB reconciliation job failing on Azure VM discovery. Change calendar inaccurate."),
        ("MuleSoft API manager rate limit misconfiguration", "MuleSoft API rate limit misconfiguration throttling client portal APIs during UAT."),
        ("Salesforce Experience Cloud login branding broken", "Salesforce Experience Cloud login page CSS broken after release. Client UAT blocked."),
        ("OutSystems mobile app crash on offline sync", "OutSystems client mobile app crashes on offline sync after platform upgrade."),
        ("Guidewire ClaimCenter UI slowness on search", "Guidewire ClaimCenter claim search exceeds 30 seconds. Adjusters cannot process backlog."),
        ("MySQL Galera cluster split-brain warning", "MySQL Galera cluster split-brain warning on insurance policy DB. Writes paused."),
        ("Azure SQL managed instance long transaction blocking", "Azure SQL MI blocking chain on policy billing schema during month-end."),
        ("Teradata AMP skew on client warehouse job", "Teradata AMP skew causing 4 hour runtime on client loyalty warehouse job."),
        ("Elasticsearch index rollover failing on observability", "Elasticsearch index rollover failing on client observability cluster. Disk 92 percent."),
        ("HashiCorp Vault namespace policy denying CI pipeline", "Vault namespace policy denying CI pipeline secret read after policy refactor."),
        ("Saviynt access review campaign overdue for offshore team", "Saviynt access review overdue for offshore delivery team. SOX finding risk."),
        ("Client VPN profile corrupt after certificate push", "Client VPN profile corrupt after automated certificate push. Consultants locked out."),
        ("LDAP bind failures on legacy IAM bridge", "LDAP bind failures on legacy IAM bridge synchronizing contractor accounts."),
        ("Privileged access break-glass account locked", "Break-glass admin account locked after password policy change. Sev1 change blocked."),
        ("SD-WAN path selection sending traffic via expensive link", "SD-WAN sending Mumbai-Poland traffic via expensive backup link. Latency 280ms."),
        ("Site-to-site VPN down between client DC and Capgemini SOC", "IPsec VPN down between client datacenter and Capgemini SOC. SIEM ingestion stopped."),
        ("Wi-Fi captive portal certificate expired at delivery centre", "Guest Wi-Fi captive portal TLS certificate expired at delivery centre. Visitors cannot join."),
        ("Core switch VRRP master flapping after VLAN change", "Core switch VRRP master flapping after VLAN restructuring. Inter-floor connectivity unstable."),
        ("Hyperconverged node disk failure in client private cloud", "Nutanix node disk failure in client private cloud hosting UAT environment."),
        ("Windows patch failure on Citrix VDI golden image", "Citrix VDI golden image patch failure prevents new desktop provisioning."),
        ("Backup job failed on client SharePoint migration share", "Veeam backup job failed on SharePoint migration staging share. Delta sync at risk."),
        ("NetApp volume nearly full on project artifact share", "NetApp volume 96 percent full on project artifact share. Build pipeline uploads failing."),
        ("Security incident: phishing targeting offshore onboarding inbox", "Security incident: phishing campaign targeting offshore onboarding shared mailbox with fake HR forms."),
        ("Security incident: unauthorized USB on client audit laptop", "Security incident: DLP blocked unauthorized USB copy on client audit laptop at client site."),
    ],
}


def _acceptable(hand: str) -> list[str]:
    if hand == "1":
        return ["1", "2"]
    if hand == "3":
        return ["3"]
    return ["2", "3"] if hand == "2" else [hand]


def main() -> None:
    cases: list[dict] = []
    for prefix, firm, office in FIRMS:
        titles = TEMPLATES[firm]
        for i, ((title, desc_suffix), (dept, hand, cat)) in enumerate(
            zip(titles, DEPT_PLAN), start=1
        ):
            case_id = f"{prefix}{i:02d}"
            if cat == "Security":
                title = title if title.startswith("Security incident:") else f"Security incident: {title.lower()}"
            desc = (
                f"{firm} {office}: {desc_suffix} "
                f"Business impact on client delivery timeline. Need IT support triage and resolution."
            )
            cases.append(
                {
                    "id": case_id,
                    "firm": firm,
                    "title": title,
                    "description": desc,
                    "urgency": "critical" if cat == "Security" or i <= 3 else "high" if i <= 12 else "medium",
                    "expect": {"hand": hand, "department": dept, "category": cat},
                    "acceptable_hands": _acceptable(hand),
                    "notes": f"{firm} {dept}",
                }
            )

    payload = {
        "version": 1,
        "description": (
            "Jury100 — Nasscom self-evaluation suite. 100 office/technology tickets: "
            "Microsoft, HSBC Tech, JPMorgan Tech, Capgemini (25 each). "
            "Clear titles and descriptions. Security tickets prefixed 'Security incident:'."
        ),
        "firms": [f[1] for f in FIRMS],
        "cases": cases,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
