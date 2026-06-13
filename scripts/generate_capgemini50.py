#!/usr/bin/env python3
"""Generate Capgemini 50-ticket scenario file."""
import json
from pathlib import Path

CASES = [
    ("CG01", "Cannot Login to Capgemini MyWizard Portal", "Cannot login to Capgemini MyWizard employee portal after password reset. Self-service portal shows 'Invalid credentials'. Need access to submit weekly timesheet before Friday cutoff.", "medium", "Access Management", "Access Management", "1", ["1", "2"], "Access / MyWizard login"),
    ("CG02", "Client VPN FortiClient Connection Failed Error 201", "FortiClient VPN to client Barclays environment fails with Error 201 authentication failed. Required for sprint demo with client stakeholders at 3 PM IST.", "high", "Network", "Network", "2", ["1", "2"], "Network / client VPN"),
    ("CG03", "Ransomware Detected on Project Laptop", "Security incident: CrowdStrike detected ransomware encryption on developer laptop. Project source code folder files renamed with .encrypted extension. Machine isolated from network.", "high", "SecOps", "Security", "3", ["3"], "Security / ransomware"),
    ("CG04", "Company Laptop Screen Flickering After Dock Connect", "Capgemini-issued laptop screen flickers when connected to USB-C dock. Undocked display is fine. Affects daily client standup presentations.", "medium", "Hardware", "Infrastructure", "2", ["1", "2"], "Hardware / dock display"),
    ("CG05", "SAP S4HANA Transport Import Failed in QA", "SAP S4HANA transport import failed in client QA system with error 'Import cancelled due to object lock'. Blocking UAT sign-off for finance module.", "high", "Software", "Application", "2", ["1", "2"], "Application / SAP transport"),
    ("CG06", "PostgreSQL Connection Pool Exhausted on Microservice", "PostgreSQL connection pool exhausted on client-order-service. API returning HTTP 500 errors. All 50 connections in use, no idle connections available.", "high", "DBA", "Database", "2", ["2", "3"], "Database / Postgres pool"),
    ("CG07", "New Contractor Okta and Jira Provisioning", "New contractor joining client agile team Monday — need Okta SSO account, Jira project access, Confluence space, and client VPN profile per onboarding form ONB-CG-331.", "medium", "Access Management", "Access Management", "2", ["1", "2"], "Access / contractor onboarding"),
    ("CG08", "Floor Printer Paper Jam Cannot Print Deliverable", "HP printer on Bangalore EPIP campus Floor 5 has paper jam. Red jam light on, print queue stuck with 12 documents including client status report.", "medium", "Hardware", "Infrastructure", "1", ["1", "2"], "Hardware / printer jam"),
    ("CG09", "Microsoft Teams Breakout Rooms Not Working", "Microsoft Teams breakout rooms fail to open during client workshop. Organizer sees 'Something went wrong' error. Main meeting audio works fine.", "medium", "Software", "Application", "2", ["1", "2"], "Application / Teams breakout"),
    ("CG10", "Firewall Whitelist Client API Endpoint Port 8443", "Need firewall rule to whitelist client API endpoint payments.clientcorp.com on port 8443 from Capgemini dev subnet. Approved in change request CR-CG-2290.", "high", "Network", "Network", "2", ["2", "3"], "Network / firewall whitelist"),
    ("CG11", "Phishing Email Mimicking Capgemini HR Payroll", "Security incident: multiple consultants received phishing email mimicking Capgemini HR payroll with malicious link. Four employees clicked before IT broadcast warning.", "high", "SecOps", "Security", "3", ["3"], "Security / HR phishing"),
    ("CG12", "Oracle Database Tablespace ORADATA 97 Percent Full", "Oracle database ORADATA tablespace at 97% on client production DB. Batch jobs failing with ORA-01653. Client SLA breach risk for nightly processing.", "high", "DBA", "Database", "2", ["2", "3"], "Database / Oracle space"),
    ("CG13", "Resigned Consultant Revoke All Client Access", "Consultant resigned effective today — immediate offboarding: disable AD, revoke Okta, client VPN, GitHub org, Jira, and ServiceNow access per HR exit ticket.", "high", "Access Management", "Access Management", "2", ["2", "3"], "Access / offboarding"),
    ("CG14", "Campus Wi-Fi Authentication Failing Pune Hinjewadi", "Corporate Wi-Fi at Pune Hinjewadi campus rejects valid credentials with 'Authentication server timeout'. Wired port on same desk works normally.", "high", "Network", "Network", "2", ["1", "2"], "Network / campus Wi-Fi"),
    ("CG15", "Salesforce Lightning Page Blank After Sandbox Refresh", "Salesforce Lightning Experience loads blank white page after client sandbox refresh. Classic view works when switched manually. Affects CRM demo for client.", "high", "Software", "Application", "2", ["1", "2"], "Application / Salesforce"),
    ("CG16", "Laptop Battery Drains to Zero in 30 Minutes", "Company laptop battery drains from 100% to 0% in 30 minutes even when plugged in. Power adapter connected, charging LED flickers. Need replacement for client site visit.", "medium", "Hardware", "Infrastructure", "2", ["1", "2"], "Hardware / battery"),
    ("CG17", "Production API Keys Exposed in GitLab Repository", "Security incident: GitLab secret detection found production AWS access keys in client project repository. Merge request was approved by 3 reviewers before alert.", "high", "SecOps", "Security", "3", ["3"], "Security / secret leak"),
    ("CG18", "MongoDB Replica Set Secondary Not Syncing", "MongoDB replica set secondary node stuck in RECOVERING state. Primary node healthy but read queries failing on secondary. Client reporting dashboard stale.", "high", "DBA", "Database", "2", ["2", "3"], "Database / MongoDB replica"),
    ("CG19", "ServiceNow Incident Form Submit Button Spins", "ServiceNow incident form submit spins indefinitely after filling all mandatory fields. No error message. Other ServiceNow modules load correctly in same session.", "medium", "Software", "Application", "2", ["1", "2"], "Application / ServiceNow"),
    ("CG20", "MFA Authenticator Lost Need Device Re-Enrollment", "Lost phone with Microsoft Authenticator MFA app. Cannot login to corporate email or client VPN until new device enrolled. Manager confirmed identity via HR.", "high", "Access Management", "Access Management", "2", ["1", "2"], "Access / MFA re-enroll"),
    ("CG21", "MPLS Circuit Down Mumbai to Client Data Center", "MPLS WAN circuit between Mumbai delivery center and client data center down since 7 AM IST. Offshore team cannot reach client staging environment.", "high", "Network", "Network", "2", ["2", "3"], "Network / MPLS outage"),
    ("CG22", "Docker Desktop Won't Start After Windows Update", "Docker Desktop fails to start with WSL2 error after Windows 11 KB update. Needed for local container development on client microservices project.", "medium", "Software", "Application", "2", ["1", "2"], "Application / Docker"),
    ("CG23", "USB Headset Microphone Not Working on Teams Calls", "Jabra USB headset microphone not detected in Microsoft Teams calls. Headset works in Windows sound settings test. Colleagues cannot hear me on client calls.", "medium", "Hardware", "Infrastructure", "2", ["1", "2"], "Hardware / headset"),
    ("CG24", "Snowflake Warehouse Suspended Credit Quota Hit", "Snowflake analytics warehouse WH_CLIENT suspended — credit quota exhausted. Client ETL pipelines and Tableau dashboards failing since midnight batch run.", "high", "DBA", "Database", "2", ["2", "3"], "Database / Snowflake"),
    ("CG25", "Unauthorized RDP Login From Foreign IP Address", "Security incident: SIEM alert shows successful RDP login to project jump server from IP 185.220.101.47 at 2:30 AM IST. No approved travel for that user.", "high", "SecOps", "Security", "3", ["3"], "Security / unauthorized RDP"),
    ("CG26", "Power BI Report Refresh Failed Gateway Offline", "On-premises Power BI data gateway shows offline in Power BI Service. All client dashboards failed scheduled refresh since 6 AM IST.", "high", "Software", "Application", "2", ["1", "2"], "Application / Power BI"),
    ("CG27", "NetApp Snapshot Restore for Deleted Project Files", "Client project files accidentally deleted from NetApp NAS share. Need snapshot restore from last night 11 PM before client audit on Thursday.", "high", "DBA", "Storage", "2", ["2", "3"], "Storage / NetApp restore"),
    ("CG28", "Intune Device Non-Compliant Blocking Outlook Mobile", "Intune marks iPhone as non-compliant — Outlook mobile cannot sync email. Device encryption on but policy shows false positive jailbreak detection.", "medium", "Software", "Application", "2", ["1", "2"], "Application / Intune MDM"),
    ("CG29", "DHCP Scope Exhausted Floor 8 Bangalore Campus", "Users on Bangalore EPIP campus Floor 8 report 'No IP address assigned'. DHCP scope 10.28.0.0/24 shows zero available leases since morning.", "high", "Network", "Network", "2", ["2", "3"], "Network / DHCP exhausted"),
    ("CG30", "Jenkins CI Pipeline Maven Build Failing", "Jenkins CI pipeline for client payment microservice failing at Maven compile step. Dependency resolution error. Last successful build 3 days ago.", "high", "Software", "Application", "2", ["1", "2"], "Application / Jenkins CI"),
    ("CG31", "Smart Badge Denied at Mumbai Office Main Gate", "Employee smart badge denied at Mumbai Airoli campus main gate turnstile with red LED. Badge works for cafeteria but not building entry since reissue.", "medium", "Access Management", "Access Management", "2", ["1", "2"], "Access / smart badge"),
    ("CG32", "Redis Cache Cluster Node Down Connection Timeout", "Redis cluster node redis-cache-03 down. Application logs show connection timeouts. API latency increased from 200ms to 5 seconds on client portal.", "high", "DBA", "Database", "2", ["2", "3"], "Database / Redis"),
    ("CG33", "Laptop Blue Screen MEMORY_MANAGEMENT After Update", "Company laptop BSOD with stop code MEMORY_MANAGEMENT after Windows update. Cannot boot into Windows. Need urgent replacement for client workshop tomorrow.", "high", "Hardware", "Infrastructure", "2", ["2", "3"], "Hardware / BSOD"),
    ("CG34", "Azure DevOps Pipeline Release Stuck Deploying", "Azure DevOps release pipeline stuck at 'Deploying to staging' for 4 hours. No error in logs. Client UAT environment unreachable from pipeline agent.", "high", "Software", "Application", "2", ["1", "2"], "Application / Azure DevOps"),
    ("CG35", "DLP Alert Sensitive Client Data in Email Attachment", "Security incident: DLP flagged email with client PII data sent to personal Gmail address. Employee attached customer database export by mistake.", "high", "SecOps", "Security", "3", ["3"], "Security / DLP violation"),
    ("CG36", "Cisco AnyConnect VPN Error 807 From Home Office", "Cisco AnyConnect VPN fails with Error 807 from home office. Cannot reach Capgemini internal tools or client staging server. Internet works fine.", "medium", "Network", "Network", "2", ["1", "2"], "Network / VPN 807"),
    ("CG37", "SharePoint Document Library Upload Fails Large File", "SharePoint client project site upload fails at 95% for 1.5GB deliverable archive. Error 'Something went wrong'. Smaller files upload successfully.", "medium", "Software", "Application", "2", ["1", "2"], "Application / SharePoint upload"),
    ("CG38", "Dual Monitor Second Screen Not Detected on Dock", "Second Dell monitor not detected when laptop connected to USB-C dock. Display settings show one screen only. Needed for dual-screen client development.", "medium", "Hardware", "Infrastructure", "2", ["1", "2"], "Hardware / dual monitor"),
    ("CG39", "MySQL Replication Lag 4 Hours on Reporting DB", "MySQL replication lag 4 hours on client reporting replica. MIS dashboards showing stale data. SQL thread running but relay log apply slow.", "high", "DBA", "Database", "2", ["2", "3"], "Database / MySQL replication"),
    ("CG40", "Grant Jira Admin Access for Project Lead", "Project lead needs Jira administrator access for client project board per approved ServiceNow request. Temporary 30-day elevation with manager sign-off.", "medium", "Access Management", "Access Management", "2", ["1", "2"], "Access / Jira admin"),
    ("CG41", "Kafka Consumer Lag 500K Messages Trade Feed", "Apache Kafka consumer group lag exceeding 500,000 messages on client trade-feed topic. Downstream analytics not receiving real-time data.", "high", "Software", "Application", "2", ["2", "3"], "Application / Kafka lag"),
    ("CG42", "Veeam Backup Job Failed Repository Out of Space", "Veeam backup job Nightly-VM-Client failed — backup repository volume full. Last successful backup 5 days ago. Client DR compliance at risk.", "high", "DBA", "Storage", "2", ["2", "3"], "Storage / Veeam backup"),
    ("CG43", "Webex Desktop One-Way Audio on Client Call", "Cisco Webex desktop — client hears me but I cannot hear them on daily scrum. Webex browser version has two-way audio on same laptop.", "medium", "Software", "Application", "2", ["1", "2"], "Application / Webex audio"),
    ("CG44", "PCI Card Numbers Found in Application Debug Logs", "Security incident: Splunk detected full credit card numbers in payment service debug logs on app-pay-stg-01. Debug logging left enabled in staging.", "high", "SecOps", "Security", "3", ["3"], "Security / PCI in logs"),
    ("CG45", "Internal DNS Not Resolving client.corp.local", "Users cannot resolve client.corp.local hostnames since 10 AM IST. External websites load fine. Affects client API integration testing.", "high", "Network", "Network", "2", ["2", "3"], "Network / DNS outage"),
    ("CG46", "AutoCAD License Checkout Failed FlexLM Timeout", "AutoCAD 2024 license checkout failed — FlexLM server timeout. Cannot open client architectural drawings for review. Server ping succeeds.", "high", "Software", "Application", "2", ["1", "2"], "Application / AutoCAD license"),
    ("CG47", "Zebra Label Printer Offline in Project Lab", "Zebra ZT410 label printer shows offline in Windows. Project lab cannot print shipping labels for client hardware deployment.", "medium", "Hardware", "Infrastructure", "2", ["1", "2"], "Hardware / label printer"),
    ("CG48", "Elasticsearch Cluster Red Status Shard Unassigned", "Elasticsearch cluster status RED — 12 unassigned shards on client search index. Product search API returning empty results on client e-commerce portal.", "high", "DBA", "Database", "2", ["2", "3"], "Database / Elasticsearch"),
    ("CG49", "Citrix VDI Published App Disconnects Every 15 Min", "Citrix Workspace published client SAP app disconnects every 15 minutes with 'Connection to server lost'. Other published apps work normally.", "high", "Software", "Application", "2", ["1", "2"], "Application / Citrix VDI"),
    ("CG50", "SSL Certificate Expired on Client Portal Staging", "Security incident: client staging portal shows NET::ERR_CERT_DATE_INVALID. SSL certificate expired yesterday. Client UAT testing blocked.", "high", "SecOps", "Security", "3", ["2", "3"], "Security / cert expiry"),
]

def main():
    cases = []
    for row in CASES:
        cid, title, desc, urg, dept, cat, hand, acc_hands, notes = row
        cases.append({
            "id": cid,
            "title": title,
            "description": desc,
            "urgency": urg,
            "expect": {"hand": hand, "department": dept, "category": cat},
            "acceptable_hands": acc_hands,
            "notes": notes,
        })
    out = {
        "version": 1,
        "description": "50 clear Capgemini consulting & delivery IT helpdesk scenarios (Set CG)",
        "cases": cases,
    }
    path = Path("data/set_capgemini50_scenarios.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {path} with {len(cases)} cases")

if __name__ == "__main__":
    main()
