# Firm 30 — SAARTHI Routing Report

- **Tickets routed:** 30
- **Department accuracy:** 27/30 (90.0%)
- **Category accuracy:** 27/30 (90.0%)
- **Hand accuracy:** 21/30 (70.0%)

## Hand distribution

- **Self-Help (Hand 1):** 1
- **Team Assist (Hand 2):** 25
- **Specialist (Hand 3):** 4

## Per-ticket results

### TF01 ✓
- **Title:** Microsoft 365 password reset link expired
- **Description:** Cannot reset Microsoft 365 password because the self-service reset link expired after 24 hours. Need account unlocked to submit monthly expense report before finance close.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Self-Help (Hand 1) — expected Hand 1
- **Confidence (C_total):** 0.727
- **Classifier:** rag (high)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: hand1_playbook; RAG similarity 0.71 (trusted)

### TF02 ✓
- **Title:** Google Workspace account locked after failed logins
- **Description:** Google Workspace corporate account locked after five failed login attempts on a company Chromebook. Need Gmail and Drive access restored before a client presentation at 2 PM IST.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.658
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.70 (trusted)

### TF03 ✓
- **Title:** AWS Client VPN authentication failed
- **Description:** AWS Client VPN to the Amazon internal environment fails with authentication error 801. Need VPN access for a production deployment review with the SRE team at 4 PM IST.
- **Expected team:** Network | **Actual team:** Network
- **Expected category:** Network | **Actual category:** Network
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.615
- **Classifier:** rag (medium)
- **Reason:** Classifier: Network (rag); Supervisor policy: c_total_band; RAG similarity 0.62 (trusted)

### TF04 ✓
- **Title:** Meta Workplace SSO redirect loop
- **Description:** Meta Workplace portal is stuck in an SSO redirect loop after a recent password change. Cannot access the internal wiki or submit a PTO request.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.645
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.68 (trusted)

### TF05 ✗
- **Title:** Apple Mac FileVault recovery key forgotten
- **Description:** Forgot the FileVault recovery key for an Apple corporate MacBook Pro. The laptop boots to the recovery screen and needs unlock before the morning standup.
- **Expected team:** Access Management | **Actual team:** Hardware
- **Expected category:** Access Management | **Actual category:** Infrastructure
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Infrastructure (keyword); Supervisor policy: low_grounding; RAG similarity 0.70 (low_title_overlap)

### TF06 ✓
- **Title:** Netflix internal portal password expired
- **Description:** Netflix internal employee portal password has expired. The self-service reset page shows a policy violation error and travel reimbursement approval is blocked.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Access Management (keyword); Supervisor policy: low_grounding; RAG similarity 0.70 (low_title_overlap)

### TF07 ✓
- **Title:** Nvidia CUDA driver crash on training workstation
- **Description:** Nvidia CUDA driver crashes repeatedly on an ML training workstation during model fine-tuning. Error shown: nvlddmkm display driver stopped responding. GPU cluster job submission is blocked.
- **Expected team:** Software | **Actual team:** Software
- **Expected category:** Application | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG similarity 0.60 (low_title_overlap)

### TF08 ✓
- **Title:** Intel docking station not detecting dual monitors
- **Description:** Intel office ThinkPad docking station fails to detect dual monitors after a Windows update. USB-C dock LED blinks amber and dual-screen setup is needed for a code review.
- **Expected team:** Hardware | **Actual team:** Hardware
- **Expected category:** Infrastructure | **Actual category:** Infrastructure
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Infrastructure (keyword); Supervisor policy: low_grounding; RAG similarity 0.56 (low_title_overlap)

### TF09 ✓
- **Title:** Oracle Autonomous Database connection timeout
- **Description:** Oracle Autonomous Database connections are timing out from the reporting service with ORA-12170 TNS connect timeout. Finance batch jobs are blocked for quarter-end close.
- **Expected team:** DBA | **Actual team:** DBA
- **Expected category:** Database | **Actual category:** Database
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Database (keyword); Supervisor policy: low_grounding; RAG similarity 0.59 (low_title_overlap)

### TF10 ✓
- **Title:** SAP Fiori launchpad not loading after patch
- **Description:** SAP Fiori launchpad fails to load after SAP GUI 8.0 patch and shows a blank white screen. Cannot access the procurement module for PO approval.
- **Expected team:** Software | **Actual team:** Software
- **Expected category:** Application | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG similarity 0.54 (below_medium)

### TF11 ✓
- **Title:** Salesforce SSO login loop on production org
- **Description:** Salesforce production org SSO login loops indefinitely after an Okta password change. Cannot access the opportunity pipeline before the QBR at 5 PM IST.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.639
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.67 (trusted)

### TF12 ✓
- **Title:** Adobe Creative Cloud license activation failed
- **Description:** Adobe Creative Cloud license activation fails with error 205 on a design workstation. Photoshop and Illustrator show no active subscription and a design deliverable is due today.
- **Expected team:** Software | **Actual team:** Software
- **Expected category:** Application | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.360
- **Classifier:** keyword (low)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG similarity 0.56 (low_title_overlap)

### TF13 ✓
- **Title:** Cisco AnyConnect VPN error 440 driver failure
- **Description:** Cisco AnyConnect VPN fails with error 440 driver failure on a Windows 11 laptop. Cannot reach the corporate network or client staging environment.
- **Expected team:** Network | **Actual team:** Network
- **Expected category:** Network | **Actual category:** Network
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.627
- **Classifier:** rag (medium)
- **Reason:** Classifier: Network (rag); Supervisor policy: c_total_band; RAG similarity 0.65 (trusted)

### TF14 ✗
- **Title:** VMware vSphere host unreachable in cluster
- **Description:** VMware vSphere ESXi host vmhost-prod-07 is unreachable in the production cluster. HA failover triggered and 12 VMs migrated. Need host health check before nightly batch window.
- **Expected team:** Hardware | **Actual team:** Software
- **Expected category:** Infrastructure | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.360
- **Classifier:** keyword (low)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG similarity 0.53 (below_medium)

### TF15 ✓
- **Title:** IBM Lotus Notes mailbox access denied after migration
- **Description:** Cannot access migrated IBM Lotus Notes mailbox after Domino-to-Exchange cutover. Self-service migration portal shows mailbox not found and compliance audit email is needed.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Access Management (keyword); Supervisor policy: low_grounding; RAG similarity 0.60 (low_title_overlap)

### TF16 ✓
- **Title:** TCS Citrix Workspace session disconnects every 10 minutes
- **Description:** TCS client Citrix Workspace session disconnects every 10 minutes with error WFICA32. UAT testing on a banking client project is blocked before Friday go-live.
- **Expected team:** Software | **Actual team:** Software
- **Expected category:** Application | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.360
- **Classifier:** keyword (low)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG: no_match

### TF17 ✓
- **Title:** Infosys office printer paper jam error 13.02
- **Description:** Infosys Bangalore campus HP LaserJet shows paper jam error 13.02. Jam was cleared twice but error persists. Need to print a signed NDA for client onboarding at 11 AM.
- **Expected team:** Hardware | **Actual team:** Hardware
- **Expected category:** Infrastructure | **Actual category:** Infrastructure
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.729
- **Classifier:** rag (high)
- **Reason:** Classifier: Infrastructure (rag); Supervisor policy: c_total_band; RAG similarity 0.71 (trusted)

### TF18 ✓
- **Title:** Wipro Microsoft Teams messages not syncing
- **Description:** Microsoft Teams on a Wipro laptop is not syncing messages or calendar events since yesterday. Banner shows trouble connecting and standup invites are missing.
- **Expected team:** Software | **Actual team:** Software
- **Expected category:** Application | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG: no_match

### TF19 ✓
- **Title:** HCL SQL Server nightly backup job failed
- **Description:** HCL managed SQL Server nightly backup job failed with error 3201 cannot open backup device. Transaction log is full on prod-db-03 and finance ETL is blocked.
- **Expected team:** DBA | **Actual team:** DBA
- **Expected category:** Database | **Actual category:** Database
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Database (keyword); Supervisor policy: low_grounding; RAG similarity 0.61 (low_title_overlap)

### TF20 ✓
- **Title:** Cognizant FortiClient VPN certificate expired
- **Description:** Cognizant FortiClient VPN rejects connection because the server certificate expired yesterday. Cannot access client dev environment for sprint demo at 3 PM IST.
- **Expected team:** Network | **Actual team:** Network
- **Expected category:** Network | **Actual category:** Network
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.628
- **Classifier:** rag (medium)
- **Reason:** Classifier: Network (rag); Supervisor policy: c_total_band; RAG similarity 0.65 (trusted)

### TF21 ✓
- **Title:** Capgemini MyWizard portal invalid credentials
- **Description:** Cannot login to Capgemini MyWizard employee portal after password reset. Portal shows invalid credentials and weekly timesheet submission is due before Friday cutoff.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 1
- **Confidence (C_total):** 0.651
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.69 (trusted)

### TF22 ✓
- **Title:** Accenture client RDP access request pending three days
- **Description:** Need RDP access to an Accenture client UAT Windows server for regression testing. Access request has been pending approval for three days and go-live is blocked.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Access Management (keyword); Supervisor policy: low_grounding; RAG similarity 0.60 (low_title_overlap)

### TF23 ✗
- **Title:** Deloitte SharePoint document library access denied
- **Description:** Deloitte audit engagement SharePoint document library returns access denied for the compliance folder. Need read access to submit working papers before partner review.
- **Expected team:** Access Management | **Actual team:** Software
- **Expected category:** Access Management | **Actual category:** Application
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.420
- **Classifier:** keyword (medium)
- **Reason:** Classifier: Application (keyword); Supervisor policy: low_grounding; RAG similarity 0.59 (low_title_overlap)

### TF24 ✓
- **Title:** JPMorgan Markets trading platform account locked
- **Description:** JPMorgan Markets trading platform account locked after five failed password attempts. Need access restored before US market open at 7 PM IST.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.650
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.68 (trusted)

### TF25 ✓
- **Title:** Goldman Sachs SQL Server deadlock on risk database
- **Description:** Goldman Sachs SQL Server risk reporting database shows persistent deadlocks on VaR calculation stored procedures. Risk reports are delayed for the global risk committee.
- **Expected team:** DBA | **Actual team:** DBA
- **Expected category:** Database | **Actual category:** Database
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.735
- **Classifier:** rag (high)
- **Reason:** Classifier: Database (rag); Supervisor policy: c_total_band; RAG similarity 0.72 (trusted)

### TF26 ✓
- **Title:** HSBCnet corporate banking portal login locked
- **Description:** Cannot login to HSBCnet corporate banking portal because the account locked after three failed attempts. Need urgent access to approve supplier payments before 4 PM IST cutoff.
- **Expected team:** Access Management | **Actual team:** Access Management
- **Expected category:** Access Management | **Actual category:** Access Management
- **Hand:** Team Assist (Hand 2) — expected Hand 2
- **Confidence (C_total):** 0.653
- **Classifier:** rag (medium)
- **Reason:** Classifier: Access Management (rag); Supervisor policy: c_total_band; RAG similarity 0.69 (trusted)

### TF27 ✓
- **Title:** Stripe AWS secret key pushed to public GitHub
- **Description:** Stripe production AWS secret access key was accidentally committed to a public GitHub repository in a CI pipeline log. Key is visible in commit history and needs immediate rotation and git purge.
- **Expected team:** SecOps | **Actual team:** SecOps
- **Expected category:** Security | **Actual category:** Security
- **Hand:** Specialist (Hand 3) — expected Hand 3
- **Confidence (C_total):** 0.270
- **Classifier:** keyword (high)
- **Reason:** Classifier: Security (keyword); Supervisor policy: security_policy; RAG similarity 0.56 (low_title_overlap)

### TF28 ✓
- **Title:** Uber suspicious RDP login from foreign IP
- **Description:** SIEM alert shows successful RDP login to an Uber finance server from an unknown foreign IP at 2 AM IST. Account finance-batch-svc had no scheduled job at that time.
- **Expected team:** SecOps | **Actual team:** SecOps
- **Expected category:** Security | **Actual category:** Security
- **Hand:** Specialist (Hand 3) — expected Hand 3
- **Confidence (C_total):** 0.270
- **Classifier:** keyword (high)
- **Reason:** Classifier: Security (keyword); Supervisor policy: security_policy; RAG similarity 0.58 (low_title_overlap)

### TF29 ✓
- **Title:** Tesla ransomware note found on shared file server
- **Description:** Ransomware note DECRYPT_INSTRUCTIONS.txt found on a Tesla engineering shared file server. Multiple project folders are encrypted with .locked extension and production CAD files are affected.
- **Expected team:** SecOps | **Actual team:** SecOps
- **Expected category:** Security | **Actual category:** Security
- **Hand:** Specialist (Hand 3) — expected Hand 3
- **Confidence (C_total):** 0.270
- **Classifier:** keyword (high)
- **Reason:** Classifier: Security (keyword); Supervisor policy: security_policy; RAG similarity 0.59 (low_title_overlap)

### TF30 ✓
- **Title:** Airbnb phishing email impersonating IT password reset
- **Description:** Airbnb employee received a phishing email impersonating IT password reset with a malicious link. Three colleagues clicked the link and DLP flagged credential entry on a fake Okta page.
- **Expected team:** SecOps | **Actual team:** SecOps
- **Expected category:** Security | **Actual category:** Security
- **Hand:** Specialist (Hand 3) — expected Hand 3
- **Confidence (C_total):** 0.210
- **Classifier:** rag (medium)
- **Reason:** Classifier: Security (rag); Supervisor policy: security_policy; RAG similarity 0.61 (trusted)

## Department mismatches

- **TF05** — expected **Access Management**, got **Hardware** (Infrastructure, Hand 2, conf 0.420)
- **TF14** — expected **Hardware**, got **Software** (Application, Hand 2, conf 0.360)
- **TF23** — expected **Access Management**, got **Software** (Application, Hand 2, conf 0.420)
