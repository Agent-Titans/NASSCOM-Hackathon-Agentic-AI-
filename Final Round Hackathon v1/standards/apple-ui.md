# Apple UI principles — Streamlit layer

> **System-wide rules** (agents, APIs, audit, naming): [`APPLE_SYSTEM_DESIGN.md`](APPLE_SYSTEM_DESIGN.md)  
> This file is **UI only** — how Streamlit applies Clarity, Deference, Depth.

**Reference:** [Apple HIG — Design Principles](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)

---

## 1. Clarity

| Principle | Implementation in Streamlit |
|-----------|----------------------------|
| One primary task per page | **New ticket** page = form only; **My tickets** = list only |
| Legible type hierarchy | Custom CSS: title 28–32px, body 15–17px, caption 13px muted |
| Meaningful labels | Show **Hand 1 / 2 / 3** with plain English subtitles (“Self-help”, “With your team”, “Specialist review”) |
| Confidence | One line: “Match strength: High / Medium / Low” derived from `c_total` — not raw floats on home |

---

## 2. Deference

| Principle | Implementation |
|-----------|----------------|
| Content first | Minimize sidebar chrome; use wide main column |
| Neutral chrome | Background `#f5f5f7`, cards white, accent `#0071e3` (align with LLD HTML docs) |
| No agent jargon | Hide pipeline step names from requester; assignee sees “Suggestions” not “Resolver output” |

---

## 3. Depth

| Principle | Implementation |
|-----------|----------------|
| Hierarchy | List → detail navigation; breadcrumb: `My tickets › TICKET-123` |
| Motion sparingly | `st.spinner` only during pipeline; success = subtle `st.success` |
| Hand-specific detail | Different detail templates per Hand (see LLD UI table) |

---

## Color semantics (outcomes)

| Semantic | Use | Hex (suggested) |
|----------|-----|-----------------|
| Success / Hand 1 | Resolved, worked | `#34c759` |
| Info / Hand 2 | Routed, in progress | `#0071e3` |
| Warning | SLA soon | `#ff9500` |
| Critical / Hand 3 | Escalation, breach | `#ff3b30` |
| Muted | Secondary text | `#6e6e73` |

---

## Components checklist (per screen)

### Requester — My tickets

- [ ] Card list with status chip + Hand badge
- [ ] Empty state with single CTA “Create ticket”
- [ ] No table with 12 columns

### Requester — New ticket

- [ ] Description (textarea), urgency (segmented: Low / Medium / High)
- [ ] One **Submit** button (primary)
- [ ] Processing card with estimated wait copy

### Requester — Ticket detail (by Hand)

| Hand | Show | Hide |
|------|------|------|
| 1 | Numbered steps, Worked / Did not work | Internal agent trace |
| 2 | Team name, SLA expectation, references | Full audit dump |
| 3 | Escalation status, what happens next | Auto-generated steps |

### Assignee — Queue

- [ ] Sort by priority then SLA remaining
- [ ] Overdue badge (Bucket B)

### Assignee — Detail

- [ ] Similar tickets (expandable)
- [ ] Suggested steps + “assist” label when Hand 3
- [ ] `c_total` band for triage (assignee-only)

### Admin — Audit

- [ ] Read-only table: timestamp, event_type, details
- [ ] Export CSV button (optional)

---

## Streamlit technical patterns

```python
# Pattern: inject once in app.py
st.set_page_config(page_title="IT Routing", layout="wide", initial_sidebar_state="collapsed")
# load custom CSS from assets/apple_theme.css
```

- Use `st.columns` for card grids, not dense dataframes on home
- Use `st.expander` for similar tickets and audit (depth without clutter)
- Role in `st.session_state` after login — never mix queues

---

## Accessibility (minimum)

- Sufficient contrast on chips (WCAG AA where possible)
- Icon + text labels (not color alone for Hand)
- Form fields with `help=` tooltips for urgency

---

## Anti-patterns (avoid)

- Dashboard of 6 charts on landing page
- Showing Gemini prompts to requesters
- Red/green only for Hand without text label
- Multiple primary buttons on one screen

---

## Sign-off before jury

- [ ] Three Hand demo paths each screenshot-ready
- [ ] Typography and spacing consistent across roles
- [ ] Mobile width: readable at 390px (judge phone check)
