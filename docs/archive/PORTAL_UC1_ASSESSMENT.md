# SAARTHI — Use Case 1 Portal Assessment

**Date:** 2026-06-12  
**Scope:** Full portal smoke test + 30-ticket routing run (no triage) + admin UI fixes  
**Demo credentials:** `1234` for all accounts

---

## Executive score (jury-style)

| Area | Score | Max | Notes |
|------|------:|----:|-------|
| UC1 — Classify & route | **8** | 10 | 80% on 30-ticket suite; Security ambiguity remains |
| UC1 — Hand 1/2/3 resolution | **8** | 10 | Playbook + supervisor bands work; some H1/H2 swaps acceptable |
| UC1 — Confidence & audit | **9** | 10 | Admin audit log, confidence %, RAG match in export |
| Employee portal | **8** | 10 | Create, detail, worked / didn't work escalation |
| Agent workspace | **8** | 10 | Dept queues, filters, assign/release/resolve |
| Admin console | **8** | 10 | KPI dashboard, aligned tables, CSV export (post-fix) |
| Auto-assign | **7** | 10 | Works after grace window; not instant on create |
| RAG / historical corpus | **9** | 10 | 1k syn corpus + Chroma; trusted gate |
| Security / guardrail | **8** | 10 | Force H3 on confirmed incidents; S01/S04/S06 gaps |
| Demo readiness | **8** | 10 | Stable sign-in, three portals, live pipeline |

**Overall estimated jury score: ~81/100 (B+ / Strong demo)**

---

## What works (requirements met)

### Use Case 1 — Ticket routing & resolution

- **5-agent pipeline:** Guardrail → Classifier → Router → Resolver → Supervisor
- **7 categories → 6 department queues** (Hardware, Software, Network, SecOps, Access Mgmt, DBA)
- **Hand 1:** Self-help steps on employee portal; `Worked` / `Did not work` feedback
- **Hand 2:** Routed to department queue; agent assign / release / resolve
- **Hand 3:** Security policy force-escalation; specialist queue
- **RAG:** Chroma + synthetic corpus; similarity gate; audit `rag_hit` / `rag_miss`
- **Confidence:** `c_total` stored; UI labels Strong / Good / Low; admin audit shows % + similar ticket

### Portals tested

| Portal | Login | Verified |
|--------|-------|----------|
| Employee | `pallavi@user` | Create ticket, pipeline, H1 steps, escalation |
| Agent | `subbu@employee` (Software) | Dept queue isolation, filters, take ticket |
| Admin | `admin@employee` | Dashboard KPIs, All Tickets table, Audit Log, CSV export |

### 30-ticket automated run (latest)

- **24/30 pass (80%)** — direct routing, no triage queue
- **Network 8/8**, **Application 7/8**, **Infrastructure 6/8**, **Security 2/6**
- Failures: I04, I05, A07, S01, S04, S06 (category/dept ambiguity)

### Admin fixes applied this session

- **All Tickets** now uses same **HTML table layout** as Audit Log (no broken `st.columns` rows)
- **Dashboard top spacing** reduced (fixed nav + header alignment)
- **Nav buttons** (Dashboard / All Tickets / Audit Log) aligned consistently
- **Export / Refresh** header buttons aligned with page title
- **Ticket detail** via select + View on All Tickets page

---

## Gaps for higher points

### P0 — Would move score to ~90+

1. **Security classifier hardening** — S01 (login → Access Mgmt), S04 (DLP → Storage), S06 (SQLi → Database). Add incident markers + Security policy bypass for ambiguous login/DLP/WAF cases.
2. **Infrastructure vs Network bleed** — I04 Secure Boot → Network; tighten classifier prompts for firmware/driver on laptop → Hardware.
3. **Application vs Network** — A07 Power BI gateway timeout → Network; disambiguate "gateway" in app context.

### P1 — Polish & jury narrative

4. **Auto-assign visibility** — 10-minute grace is correct but invisible; show "Assigning in ~Xm" or assign on agent portal refresh for demo.
5. **Admin row click** — All Tickets uses select + View; ideal: single-click row like enterprise ITSM.
6. **SecOps display label** — Show "Security" in UI while keeping SecOps internally.
7. **Hand expectation flexibility** — N02 expects H2 but gets H1 (playbook); document as acceptable or tune supervisor bands for demo.

### P2 — Stretch

8. **Human-in-the-loop triage** — Optional queue for uncertain routes (reverted; would help S01/A07-style cases).
9. **Playwright E2E in CI** — `tests/test_webapp_e2e.py` needs running Streamlit + Playwright.
10. **Multi-language / SSO** — Out of scope for hackathon but jury may ask.

---

## Feature checklist

| Feature | Status |
|---------|--------|
| Employee submit ticket | ✅ |
| AI classification | ✅ |
| Department routing | ✅ (80% strict) |
| Hand 1 self-help | ✅ |
| Hand 2 agent queue | ✅ |
| Hand 3 specialist | ✅ |
| Agent dept isolation | ✅ |
| Auto-assign after grace | ✅ (delayed) |
| Admin KPI dashboard | ✅ |
| Admin all tickets table | ✅ (fixed) |
| Admin audit log | ✅ |
| CSV export | ✅ |
| Guardrail / PII redaction | ✅ |
| Feedback escalation H1→H2 | ✅ |
| Comments on tickets | ✅ |
| Team presence on admin | ✅ |

---

## Recommended demo script (5 min)

1. **Employee** (`pallavi@user`) — password reset → Hand 1 steps → Worked
2. **Employee** — printer jam → Hand 2 Hardware; show department chip
3. **Agent** (`sree@employee`) — Hardware queue → Take → Resolve
4. **Employee** — security incident (USB malware) → Hand 3 SecOps
5. **Admin** — Dashboard KPIs → Audit Log → All Tickets → View detail → Export CSV

---

## Test commands

```bash
source .venv/bin/activate

# Portal smoke (19 checks)
python scripts/ui_smoke_test.py

# Nasscom firm suite (50 tickets)
python scripts/judge50_assessment.py
python scripts/judge50_assessment.py --live

# Independent master validation (50 tickets)
python scripts/master_assessment.py
python scripts/master_assessment.py --live

# Cognizant delivery suite (30 tickets)
python scripts/cognizant30_assessment.py --live

# Reports: test-reports/index.html
```
