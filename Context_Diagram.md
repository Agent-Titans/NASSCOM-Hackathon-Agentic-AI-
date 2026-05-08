# Context Diagram - IT Ticket Routing & Automated Resolution System

**Team:** Agent Titans
**Event:** NASSCOM Agentic AI Hackathon 2026
**Version:** 1.0
**Date:** May 2026

---

## 1. Purpose
A Context Diagram (Level 0 Data Flow Diagram) provides a high-level view of the system, showing the system as a single centralized process and its interactions with all external entities. It does not depict internal components, workflows, or data processing steps—only the boundaries of the system and the flow of data between the system and the outside world.

This diagram is derived from the system architecture defined in `architecture.md`.

---

## 2. System Boundary
The entire **IT Ticket Routing & Automated Resolution System** is treated as a single black-box process. Internal components (Streamlit UI, CrewAI Agents, Vector Database, LLM Integration Layer) are encapsulated within this boundary and not visible at this level.

---

## 3. External Entities
External entities are systems, users, or services that interact with the system but are not part of it.

| Entity | Description | Type |
|--------|-------------|------|
| End User (Employee) | Submits IT support tickets and receives resolution/escalation updates | Human Actor |
| IT Support Teams | Receives routed tickets, handles escalated issues, and provides manual resolution | Human Actor (Hardware Support, DevOps, Network Team, IT Helpdesk) |
| Security Team | Receives escalated security-category tickets and incident alerts | Human Actor |
| Google Gemini API | External LLM service providing AI-driven decision making for agents | Third-Party Service |
| ServiceNow (Future) | ITSM platform for ingesting tickets into the system | External System |
| Jira (Future) | Project management tool for tracking ticket status | External System |
| Slack (Future) | Messaging platform for real-time notifications | External System |
| Email (Future) | Ticket submission and status update channel via IMAP/SMTP | External System |
| LDAP/Active Directory (Future) | User authentication and directory service | External System |

---

## 4. Data Flows
All data movement between external entities and the system.

| Source | Destination | Data Description | Direction |
|--------|-------------|------------------|-----------|
| End User | System | Ticket description, urgency level, timestamp | Inbound |
| System | End User | Resolution steps, escalation status, confidence scores, SLA estimates, final ticket status | Outbound |
| Email | System | Ticket details via email submission (future) | Inbound |
| System | Email | Ticket status updates via email (future) | Outbound |
| Google Gemini API | System | LLM-generated classifications, routing decisions, resolution steps, supervision decisions | Inbound |
| System | Google Gemini API | Prompts, ticket context, agent task descriptions | Outbound |
| System | IT Support Teams | Routed ticket details (category, department, priority, SLA, resolution steps), escalation alerts | Outbound |
| System | Security Team | Escalated security tickets, incident logs, alert notifications | Outbound |
| ServiceNow | System | Ingested ticket data (future) | Inbound |
| System | Jira | Ticket tracking updates, status changes (future) | Outbound |
| System | Slack | New ticket alerts, escalation notifications (future) | Outbound |
| LDAP/AD | System | User authentication verification, directory details (future) | Inbound |
| System | LDAP/AD | Authentication requests (future) | Outbound |

---

## 5. Context Diagram Visualization

```
                                      ┌─────────────────────┐
                                      │ Google Gemini API  │
                                      │ (gemini-1.5-pro)   │
                                      └─────────┬───────────┘
                                                │ ▲
                                                │ │
                                      LLM Responses │ │ Prompts / Context
                                                │ │
                                                ▼ │
┌──────────────┐                          ┌──────────────────────────────────────────────────┐                          ┌──────────────┐
│  End User    │─── Ticket Submission ───▶│                                                  │─── Routed Tickets ──▶│ IT Support   │
│  (Employee)  │                          │  IT Ticket Routing & Automated Resolution System │                          │ Teams        │
└──────────────┘                          │  (Agent Titans, NASSCOM Hackathon 2026)          │                          └──────┬───────┘
      ▲                                    └──────────────────────────────────────────────────┘                                 │
      │                                              │ ▲                                                    Escalations │ │ Security
      └── Resolution / Status ────────────────────────┘ │                                                    ┌──────────────┘
                                                        │                                                    │ Security Team│
                                                        │                                                    └──────────────┘
                                                        │
                                              ┌─────────┴─────────┐
                                              │                   │
                                              ▼                   ▼
                                     ┌────────────────┐   ┌────────────────┐
                                     │ ServiceNow     │   │ Email (Future) │
                                     │ (Future)       │   │ (IMAP/SMTP)    │
                                     │ Ticket Ingestion│   │ Ticket Submit  │
                                     └────────────────┘   └────────────────┘
                                              ▲                   │
                                              └──── Ingested ─────┘
                                                Tickets
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ Jira (Future)  │◀── Ticket Tracking
                                     └────────────────┘
                                              ▲
                                              └── Status Updates
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ Slack (Future) │◀── Notifications
                                     └────────────────┘
                                              ▲
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ LDAP/AD        │◀── Auth Requests
                                     │ (Future)       │
                                     └────────────────┘
                                              │ ▲
                                              │ │
                                              └─ Auth Details ─┘
```

*Note: Future integrations are marked as (Future). Bidirectional flows are indicated with arrows on both ends of the line.*

---

## 6. Key Notes
1. The system's internal components (Presentation Layer, Orchestration Layer, Agent Intelligence Layer, Knowledge Layer) are encapsulated within the system boundary and not shown in this diagram.
2. All future integrations are optional and part of the system's scalability roadmap as defined in `architecture.md` (Section 9, 11).
3. The Security Team receives only escalated security-category tickets, per the system's security policy (Section 8.2 of `architecture.md`).
4. The Google Gemini API is the only external AI service used; no other LLM providers are currently integrated.
5. Data flows related to the Knowledge Layer (ChromaDB/FAISS) are internal and not visible at this context level.
