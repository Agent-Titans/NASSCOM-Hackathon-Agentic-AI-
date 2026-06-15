# Demo checklist — Use Case 1 end-to-end

Run before jury demo. App: `streamlit run src/ui/app.py` · Password: `1234`

**Bootstrap (clean RAG + 1k historical tickets + Chroma Gemini index):**
```bash
# Stop Streamlit first (avoids SQLite lock), then:
python scripts/bootstrap_rag_environment.py
```

After bootstrap: **0 live tickets**, **1000 RESOLVED `syn-*` in SQLite**, **~1006 vectors in Chroma** (KB + synthetic). See `docs/COLLEAGUE_SETUP.md` for teammate clone flow. Routing reports: `test-reports/index.html`.

Automated coverage: `python scripts/ui_smoke_test.py` · reports: `test-reports/index.html`

---

## 1. Sign-in & roles

| Step | Action | Expected |
|------|--------|----------|
| 1.1 | Open app → **Sign In** | SAARTHI welcome, unified sign-in card |
| 1.2 | `pallavi@user` / `1234` | Employee portal home |
| 1.3 | Sign out → `sree@employee` / `1234` | Agent workspace (Software queue) |
| 1.4 | Sign out → `admin@employee` / `1234` | Admin overview + Audit log nav |
| 1.5 | Bad password | Error message, no access |

---

## 2. Hand 1 — Self-help (password)

| Step | Action | Expected |
|------|--------|----------|
| 2.1 | Employee → **+ New Request** | Create form |
| 2.2 | Title: `Forgot password` · Description: password lockout | Pipeline runs (<15s) |
| 2.3 | Ticket detail | **Self-Help** badge, steps listed |
| 2.4 | Click **Worked** | Ticket closes, thank-you flash |
| 2.5 | New H1 ticket → **Did not work** | Routed notice, Hand 2, assignee set |

---

## 3. Hand 2 — Department routing

| Step | Action | Expected |
|------|--------|----------|
| 3.1 | `gajanan@user` → printer jam ticket | Hand 1 or 2 per RAG; Hardware/Software dept |
| 3.2 | Cognos / DB ticket | Team queue, department chip |
| 3.3 | Agent `hw@employee` login | Hardware queue only (no Software tickets) |
| 3.4 | Queue filter **Unassigned** | Only tickets without owner |
| 3.5 | Queue filter **Mine** | Only tickets assigned to logged-in agent |
| 3.6 | Queue filter **SLA at risk** | Tickets near SLA breach |

---

## 4. Hand 3 — Security escalation

| Step | Action | Expected |
|------|--------|----------|
| 4.1 | VPN breach / AWS key leak ticket | **Specialist** / SecOps, no fake self-help |
| 4.2 | Admin → ticket row | Hand 3 pill, SecOps department |
| 4.3 | Audit log | guardrail → classifier → router → resolver → supervisor events |

---

## 5. Confidence & audit story

| Step | Action | Expected |
|------|--------|----------|
| 5.1 | Any ticket detail | Human-readable match strength (not raw agent dump) |
| 5.2 | Admin audit log | Append-only events per agent |
| 5.3 | PII in description | Redacted in stored text / guardrail audit |

---

## 6. Routing metrics (automated)

```bash
open test-reports/index.html
```

| Metric | Target | Source |
|--------|--------|--------|
| Classifier fix (Judge100A) | ≥85% | `classifier_fix_validation_report.html` |
| Judge Pro (200) | jury-ready | `judge_pro_report.html` |
| Portal UI smoke | 19/19 pass | `scripts/ui_smoke_test.py` |

---

## 7. Agent department matrix

Log in as each agent; confirm inbox shows **only** that department's Hand 2/3 tickets.

| Email | Department | Sample ticket to seed |
|-------|------------|------------------------|
| `sree@employee` / `kiran@employee` | Hardware | Printer / charger |
| `subbu@employee` / `sruthi@employee` / `meena@employee` | Software | Application / Cognos-style |
| `narsimha@employee` / `chandana@employee` | SecOps | Security breach |
| `shashi@employee` / `rahul@employee` | Network | VPN 807 |
| `sagar@employee` / `priya@employee` | DBA (incl. Storage) | SQL / NAS backup |
| `satya@employee` | Access Management | Account lockout (H2) |

---

## Quick smoke (no UI)

```bash
python scripts/ui_smoke_test.py
bash scripts/prepare_handoff.sh
```
