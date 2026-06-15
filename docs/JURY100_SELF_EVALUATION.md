# SAARTHI Jury100 — Self-Evaluation Report

**Generated:** 2026-06-15T07:24:26.071522+00:00

## Executive summary

| Metric | Value |
|--------|-------|
| **Routing pass rate** | **51/100 (51%)** |
| **Grand score** | **65.2/100** |
| **Department macro-F1** | 0.509 |
| **Department micro-F1** | 0.51 |
| **Security H3 correct** | 8/8 |
| **Avg latency** | 14.13s (p50 15.02s, p90 17.54s) |
| **UI smoke** | PASS |

## LLM jury assessment

- **Overall:** 8.0/10 (error)
- **Verdict:** HTTP Error 429: Too Many Requests
- **Use-case alignment:** —
- **LLD alignment:** —
- **Responsible AI:** —
- **Evaluation rigor:** —

**Strengths:**

**Improvements:**

## Per-firm results

| Firm | Pass | F1 | Avg latency |
|------|------|-----|-------------|
| Capgemini | 13/25 (52%) | 0.425 | 13.65s |
| HSBC Tech | 12/25 (48%) | 0.42 | 14.38s |
| JPMorgan Tech | 12/25 (48%) | 0.494 | 14.25s |
| Microsoft | 14/25 (56%) | 0.636 | 14.26s |

## Department F1 (per label)

| Department | P | R | F1 | n |
|------------|---|---|----|---|
| Access Management | 0.636 | 0.35 | 0.452 | 20 |
| Application | 0.448 | 0.542 | 0.491 | 24 |
| Database | 0.625 | 0.5 | 0.556 | 20 |
| Infrastructure | 0.333 | 0.25 | 0.286 | 8 |
| Network | 0.444 | 0.5 | 0.471 | 16 |
| SecOps | 0.727 | 1.0 | 0.842 | 8 |
| Storage | 0.333 | 0.75 | 0.462 | 4 |

## Classify source mix

- **keyword:** 100

## Per-agent timing (avg ms)

- **classifier:** 6904ms
- **guardrail:** 3ms
- **resolution_format:** 3ms
- **resolver:** 7606ms
- **retrieval:** 362ms
- **router:** 3ms
- **supervisor:** 5ms

## Failures (49)

| ID | Firm | Title | Expected | Actual | Hand |
|----|------|-------|----------|--------|------|
| CG09 | Capgemini | Teradata AMP skew on client warehouse jo | Database | Application | H2→H2 |
| CG10 | Capgemini | Elasticsearch index rollover failing on  | Database | Storage | H2→H2 |
| CG11 | Capgemini | HashiCorp Vault namespace policy denying | Database | Application | H2→H2 |
| CG13 | Capgemini | Client VPN profile corrupt after certifi | Access Management | Network | H2→H2 |
| CG14 | Capgemini | LDAP bind failures on legacy IAM bridge | Access Management | Application | H2→H2 |
| CG16 | Capgemini | SD-WAN path selection sending traffic vi | Access Management | Network | H1→H2 |
| CG17 | Capgemini | Site-to-site VPN down between client DC  | Network | SecOps | H2→H3 |
| CG18 | Capgemini | Wi-Fi captive portal certificate expired | Network | SecOps | H2→H3 |
| CG19 | Capgemini | Core switch VRRP master flapping after V | Network | Application | H2→H2 |
| CG20 | Capgemini | Hyperconverged node disk failure in clie | Network | Storage | H2→H2 |
| CG21 | Capgemini | Windows patch failure on Citrix VDI gold | Infrastructure | Application | H2→H2 |
| CG22 | Capgemini | Backup job failed on client SharePoint m | Infrastructure | Application | H2→H2 |
| HS02 | HSBC Tech | Oracle Flexcube batch job failed overnig | Application | Database | H2→H2 |
| HS03 | HSBC Tech | Temenos Transact API timeout on loan ori | Application | Network | H2→H2 |
| HS04 | HSBC Tech | SWIFT Alliance Access message queue back | Application | Access Management | H2→H2 |
| HS06 | HSBC Tech | Db2 HADR standby lag on trade ledger | Application | Database | H2→H2 |
| HS11 | HSBC Tech | CyberArk safe access request expired | Database | Access Management | H2→H2 |
| HS12 | HSBC Tech | SailPoint identity certification campaig | Access Management | Application | H2→H2 |
| HS13 | HSBC Tech | Smart card PIN unlock for HSM operator | Access Management | Infrastructure | H2→H2 |
| HS14 | HSBC Tech | VPN token seed mismatch after phone repl | Access Management | Network | H2→H2 |
| HS16 | HSBC Tech | MPLS link congestion between HK and UK h | Access Management | Network | H1→H2 |
| HS20 | HSBC Tech | Blade server PSU fault in primary tradin | Network | Infrastructure | H2→H2 |
| HS21 | HSBC Tech | VMware vMotion failure on risk calculati | Infrastructure | Application | H2→H2 |
| HS22 | HSBC Tech | NetApp volume snapshot restore needed fo | Infrastructure | Storage | H2→H2 |
| HS23 | HSBC Tech | SAN fabric zone misconfiguration after s | Storage | Application | H2→H2 |
| JP01 | JPMorgan Tech | Athena risk report grid timeout | Application | Network | H2→H2 |
| JP02 | JPMorgan Tech | LOLR liquidity dashboard stale positions | Application | Database | H2→H2 |
| JP03 | JPMorgan Tech | Fusion platform API gateway 502 errors | Application | Network | H2→H2 |
| JP04 | JPMorgan Tech | SimCorp Dimension corporate action impor | Application | Database | H2→H2 |
| JP06 | JPMorgan Tech | Cassandra repair failing on market data  | Application | Database | H2→H2 |
| JP07 | JPMorgan Tech | Oracle Exadata cell disk offline | Database | Storage | H2→H2 |
| JP10 | JPMorgan Tech | ElasticSearch cluster red status on log  | Database | SecOps | H2→H3 |
| JP11 | JPMorgan Tech | ForgeRock SSO assertion validation failu | Database | Access Management | H2→H2 |
| JP12 | JPMorgan Tech | BeyondTrust session recording not starti | Access Management | Application | H2→H2 |
| JP16 | JPMorgan Tech | Cross-connect latency spike to NYSE matc | Access Management | Network | H1→H2 |
| JP17 | JPMorgan Tech | Multicast feed gap on US equity depth ch | Network | Storage | H2→H2 |
| JP20 | JPMorgan Tech | Trading floor UPS battery test failure | Network | Infrastructure | H2→H2 |
| JP22 | JPMorgan Tech | Isilon cluster snapshot policy not runni | Infrastructure | Storage | H2→H2 |
| MS04 | Microsoft | Power BI dataset refresh gateway offline | Application | Network | H2→H2 |
| MS06 | Microsoft | SQL Azure elastic pool DTU exhaustion | Application | Database | H2→H2 |
| MS07 | Microsoft | Cosmos DB request rate throttling alert | Database | Application | H2→H2 |
| MS10 | Microsoft | Fabric warehouse load job permission den | Database | Application | H2→H2 |
| MS11 | Microsoft | Entra ID conditional access blocks contr | Database | Access Management | H2→H2 |
| MS12 | Microsoft | Privileged Identity Management activatio | Access Management | Application | H2→H2 |
| MS13 | Microsoft | FIDO2 security key enrollment failure | Access Management | Infrastructure | H2→H2 |
| MS14 | Microsoft | Service principal secret expired for Gra | Access Management | Application | H2→H2 |
| MS16 | Microsoft | ExpressRoute BGP session down primary ci | Access Management | Network | H1→H2 |
| MS20 | Microsoft | Hyper-V cluster live migration failure | Network | Application | H2→H2 |
| MS22 | Microsoft | OneDrive sync client throttling large en | Infrastructure | Application | H2→H2 |

## Methodology

- **Pass:** correct hand (or acceptable_hands) AND correct department queue
- **Live pipeline:** Guardrail → Retrieval → Classifier (Gemini-primary) → Router → Resolver → Supervisor
- **Scenarios:** `data/set_jury100_scenarios.json` — 25 tickets × 4 firms
- **HTML report:** `test-reports/jury100_report.html`
