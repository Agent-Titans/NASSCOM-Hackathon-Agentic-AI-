# Data Flow Diagram - IT Ticket Routing & Automated Resolution System
**Team:** Agent Titans
**Event:** NASSCOM Agentic AI Hackathon 2026
**Version:** 1.0
**Date:** May 2026

---

## 1. Level 0: Context Diagram (System Boundary)
Shows the system's interaction with external entities at a high level.

```
                    ┌──────────────────┐
                    │   IT Support     │
                    │   Staff          │
                    └────────┬─────────┘
                             │ Escalated Tickets
                             │
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │  IT TICKET       │◀─────────────┐
                    │  ROUTING &       │              │
             Final │  RESOLUTION     │ Escalation    │
         Result ◀─│  SYSTEM          │ Request       │
                    │                  │              │
                    └────────┬─────────┘              │
                             │ Resolution Steps        │
                             │ Final Status            │
                             ▼                         │
                    ┌──────────────────┐               │
                    │   End User       │               │
                    │   (Ticket        │               │
                    │   Submitter)     │               │
                    └────────┬─────────┘               │
                             │ Ticket Description      │
                             │ Urgency Level           │
                             └─────────────────────────┘
```

**External Entities:**
- **End User:** Submits tickets, receives resolution/escalation status
- **IT Support Staff:** Receives escalated tickets requiring human review

---

## 2. Level 1: System-Level DFD
Shows core processes, data stores, and data flows between components.

```
                    ┌──────────────────┐
                    │  End User /     │
                    │  IT Staff       │
                    └────────┬─────────┘
                             │ 1. Ticket Description + Urgency
                             ▼
                    ┌──────────────────┐
                    │  1.0 Streamlit UI │
                    │  (Input Form +   │
                    │   Results Display)│
                    └────────┬─────────┘
                             │ 2. Structured Ticket Data
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │ 2.0         │    │  3.0        │    │ 4.0         │
  │ Classifier   │───▶│  Router     │───▶│ Resolver    │
  │ Agent       │    │  Agent      │    │ Agent       │
  └─────────────┘    └─────────────┘    └──────┬──────┘
                                                │ 5. Resolution Query
                                                ▼
                                         ┌─────────────┐
                                         │ 6.0 RAG     │
                                         │ Handler     │
                                         └──────┬──────┘
                                                │ 6. Vector DB Query
                                                ▼
                                         ┌─────────────┐
                                         │ D1: ChromaDB/│
                                         │ FAISS Vector │
                                         │ Store        │
                                         │ (Past Tickets│
                                         │  + KB Docs)  │
                                         └──────┬──────┘
                                                │ 7. Similar Tickets + KB Articles
                                                ▼
                                         ┌─────────────┐
                                         │ 6.0 RAG     │
                                         │ Handler     │
                                         └──────┬──────┘
                                                │ 8. Resolution Context
                                                ▼
                                         ┌─────────────┐
                                         │ 4.0 Resolver│
                                         │ Agent       │
                                         └──────┬──────┘
                                                │ 9. Resolution Steps + References
                                                ▼
                                         ┌─────────────┐
                                         │ 5.0         │
                                         │ Supervisor  │
                                         │ Agent       │
                                         └──────┬──────┘
                                                │ 10. Config (Thresholds, Rules)
                                                ▼
                                         ┌─────────────┐
                                         │ D3: Config  │
                                         │ Store (.env)│
                                         │ + Rules     │
                                         └─────────────┘
                                                │ 11. Final Result (JSON)
                                                ▼
                                         ┌─────────────┐
                                         │  1.0 Streamlit │
                                         │  UI (Result) │
                                         └──────┬──────┘
                                                │ 12. Resolution / Escalation Notice
                             ┌──────────────────┼──────────────────┐
                             ▼                  ▼                  ▼
                    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                    │  End User   │    │ IT Support   │    │  D2: Ticket │
                    │  (Resolution)│    │ Staff        │    │  Data Store │
                    │             │    │ (Escalation) │    │ (Processed)  │
                    └─────────────┘    └─────────────┘    └─────────────┘
```

**Process Descriptions:**
| ID | Process | Description |
|----|---------|-------------|
| 1.0 | Streamlit UI | Handles ticket submission, displays results |
| 2.0 | Classifier Agent | Categorizes tickets, assigns confidence scores |
| 3.0 | Router Agent | Routes tickets to departments, sets priority/SLA |
| 4.0 | Resolver Agent | Generates resolution steps using RAG |
| 5.0 | Supervisor Agent | Reviews outputs, decides escalation |
| 6.0 | RAG Handler | Queries vector DB for similar tickets/KB articles |

**Data Stores:**
| ID | Data Store | Description |
|----|------------|-------------|
| D1 | ChromaDB/FAISS Vector Store | Past ticket embeddings, knowledge base documents |
| D2 | Ticket Data Store | Processed ticket records with all agent outputs |
| D3 | Config Store | Environment variables, routing rules, thresholds |

---

## 3. Level 2: Agent Processing DFD
Details the sequential data flow between agents (simplified from LLD Section 4.2).

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Classifier    │    │ Router        │    │ Resolver      │    │ Supervisor    │
│ Agent         │───▶│ Agent         │───▶│ Agent         │───▶│ Agent         │
└───────────────┘    └───────────────┘    └───────────────┘    └───────────────┘
        │                      │                      │                      │
        │ 1. Classification   │ 2. Routing          │ 3. Resolution       │ 4. Final Result
        │ (Category,          │ (Department,         │ (Steps,             │ (Confidence,
        │  Subcategory,       │  Priority,           │  Estimated Time)    │  Escalation Flag,
        │  Confidence)        │  SLA)               │                      │  Resolution Steps)
        ▼                      ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              Final Output (JSON)                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Specifications
Lists all key data flows between components with their data elements.

| Flow ID | Source | Destination | Data Elements |
|---------|--------|-------------|---------------|
| 1 | End User | Streamlit UI | Ticket description, urgency level |
| 2 | Streamlit UI | Classifier Agent | Ticket description, timestamp |
| 3 | Classifier Agent | Router Agent | Category, subcategory, confidence score, reasoning |
| 4 | Router Agent | Resolver Agent | Category, subcategory, department, priority, SLA |
| 5 | Resolver Agent | RAG Handler | Category, subcategory, ticket description |
| 6 | RAG Handler | Vector DB | Query embedding, category filter |
| 7 | Vector DB | RAG Handler | Similar ticket IDs, KB article links, resolution references |
| 8 | RAG Handler | Resolver Agent | Resolution context, similar tickets, references |
| 9 | Resolver Agent | Supervisor Agent | Resolution steps, estimated time, references, reasoning |
| 10 | Config Store | All Agents | Routing maps, confidence thresholds, priority rules |
| 11 | Supervisor Agent | Streamlit UI | Final JSON with all agent outputs, escalation flag |
| 12 | Streamlit UI | End User/IT Staff | Resolution steps, escalation notice, ticket status |

---

## 5. State Transition Diagram (Ticket Lifecycle)
From LLD Section 6.1, showing ticket state changes.

```
           ┌─────────────────────────┐
           │     TICKET CREATED       │
           │   (Initial State)       │
           └───────────┬─────────────┘
                       │ Submit Ticket
                       ▼
           ┌─────────────────────────┐
           │     CLASSIFYING          │
           │   (Classifier Agent)     │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     ROUTING              │
           │   (Router Agent)         │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     RESOLVING           │
           │   (Resolver Agent)      │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     SUPERVISING         │
           │   (Supervisor Agent)    │
           └───────────┬─────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
  ┌─────────────────┐    ┌─────────────────┐
  │  RESOLVED       │    │  ESCALATED      │
  │  (Auto-         │    │  (Human         │
  │   Resolution)   │    │   Review)       │
  └────────┬────────┘    └────────┬────────┘
           │                       │
           ▼                       ▼
  ┌─────────────────┐    ┌─────────────────┐
  │  CLOSED         │    │  IN PROGRESS    │
  │  (Completed)    │    │  (Human Working)│
  └─────────────────┘    └────────┬────────┘
                                  │ Human Resolves
                                  ▼
                          ┌─────────────────┐
                          │  CLOSED         │
                          │  (After Human)  │
                          └─────────────────┘
```
