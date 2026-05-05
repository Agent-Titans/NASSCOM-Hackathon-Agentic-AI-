# Architecture Document - IT Ticket Routing & Automated Resolution System

**Team:** Agent Titans  
**Event:** NASSCOM Agentic AI Hackathon 2026  
**Version:** 1.0  
**Date:** May 2026

---

## 1. Executive Summary

The IT Ticket Routing & Automated Resolution System is a multi-agent AI solution designed to automate IT support ticket processing. It uses a sequential agent-based architecture where specialized agents handle classification, routing, resolution, and supervision of IT tickets, reducing manual intervention and improving response times.

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│                    (Streamlit Web Interface)                        │
│   - Ticket Submission Form                                         │
│   - Results Visualization                                           │
│   - Confidence Scores & Escalation Status                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                         │
│                    (CrewAI + Python Backend)                        │
│   - Agent Coordination                                             │
│   - Sequential Workflow Management                                  │
│   - Data Transformation                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ CLASSIFIER   │    │   ROUTER     │    │  RESOLVER    │
│   AGENT      │───▶│   AGENT      │───▶│   AGENT      │
│              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ SUPERVISOR   │
                                        │   AGENT      │
                                        │              │
                                        └──────┬───────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        INTELLIGENCE LAYER                          │
│              (Google Gemini / GPT + LangChain)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE LAYER                             │
│              (ChromaDB / FAISS Vector Database)                    │
│   - Past Ticket Embeddings                                        │
│   - Knowledge Base Documents                                      │
│   - Similar Ticket Retrieval (RAG)                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architectural Principles

| Principle | Description |
|-----------|-------------|
| **Modularity** | Each agent is a standalone module with defined inputs/outputs |
| **Sequential Processing** | Agents execute in a defined order with clear handoff |
| **Scalability** | New agents can be added without disrupting existing flow |
| **Explainability** | Each agent provides reasoning for its decisions |
| **Human-in-the-Loop** | Supervisor agent decides when human intervention is needed |

---

## 3. Layer-by-Layer Architecture

### 3.1 Layer 1: Presentation Layer (Streamlit UI)

**Purpose:** Provide an intuitive web interface for ticket submission and results visualization.

**Components:**
- `app.py` - Main Streamlit application
- Ticket submission form with fields for description, urgency, etc.
- Results dashboard showing category, department, priority, resolution steps
- Confidence score visualization
- Escalation status indicator

**Technologies:**
- Streamlit 1.28.0
- Python 3.9+

### 3.2 Layer 2: Orchestration Layer (CrewAI + Python)

**Purpose:** Coordinate the sequential execution of agents and manage data flow.

**Components:**
- Agent initialization and configuration
- Sequential workflow: Classifier → Router → Resolver → Supervisor
- Data transformation between agents
- Error handling and logging

**Technologies:**
- CrewAI 0.1.0
- Python-dotenv for configuration

### 3.3 Layer 3: Agent Intelligence Layer

**Purpose:** Provide AI-driven decision making for each agent.

**Agents:**

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **Classifier** | Categorize tickets | Ticket description | Category, subcategory, confidence |
| **Router** | Route to department | Category, urgency | Department, team, priority, SLA |
| **Resolver** | Generate solutions | Category, subcategory | Resolution steps, estimated time |
| **Supervisor** | Quality assurance | All agent outputs | Final decision, escalation flag |

**Technologies:**
- LangChain 0.1.0
- Google Gemini API (gemini-1.5-pro)
- LangChain Google GenAI integration

### 3.4 Layer 4: Knowledge Layer (RAG + Vector Database)

**Purpose:** Provide historical context and similar ticket references.

**Components:**
- Vector embeddings of past tickets
- Knowledge base documents
- RAG (Retrieval Augmented Generation) handler

**Technologies:**
- ChromaDB 0.4.0 (primary)
- FAISS 1.7.4 (alternative)
- Sentence transformers for embeddings

### 3.5 Layer 5: Decision & Policy Layer

**Purpose:** Define business rules and escalation policies.

**Policies:**
- Confidence threshold: 0.75 (configurable via `CONFIDENCE_THRESHOLD`)
- Security tickets always escalated
- Critical priority tickets escalated
- Low-confidence tickets (< 0.75) escalated

---

## 4. Data Architecture

### 4.1 Ticket Data Model

```
Ticket
├── ticket_id: str (unique identifier)
├── description: str (user's problem description)
├── urgency: str (Low/Medium/High/Critical)
├── timestamp: datetime (submission time)
├── classification: dict
│   ├── category: str (Hardware/Software/Network/Security/HR/IT Access)
│   ├── subcategory: str (Printer/Monitor/Application/VPN/etc.)
│   ├── confidence_score: float (0.0 - 1.0)
│   └── reasoning: str
├── routing: dict
│   ├── department: str
│   ├── team: str
│   ├── priority: str
│   ├── sla_hours: int
│   └── reasoning: str
├── resolution: dict
│   ├── resolution_steps: list[str]
│   ├── estimated_time: str
│   └── references: list[str]
├── supervision: dict
│   ├── confidence: float
│   ├── escalate: bool
│   ├── escalation_reason: str
│   └── supervisor_notes: str
└── metadata: dict
    ├── processing_status: str
    ├── requires_human_review: bool
    └── similar_tickets: list[str]
```

### 4.2 Data Flow

```
User Input (ticket description + urgency)
        │
        ▼
┌───────────────────────┐
│   Classifier Agent    │
│   - Keyword matching  │
│   - Category scoring  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    Router Agent       │
│   - Department map    │
│   - Priority calc     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   Resolver Agent      │
│   - Solution lookup   │
│   - RAG retrieval     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Supervisor Agent     │
│   - Confidence calc   │
│   - Escalation check │
└───────────┬───────────┘
            │
            ▼
    Final Result (JSON)
            │
            ▼
    Streamlit UI Display
```

---

## 5. Agent Interaction Architecture

### 5.1 Sequential Communication Pattern

```python
# Agent Pipeline Execution
classifier = ClassifierAgent()
router = RouterAgent()
resolver = ResolverAgent()
supervisor = SupervisorAgent()

# Sequential flow with data passing
classification = classifier.classify(ticket_description)
routing = router.route(classification, urgency)
resolution = resolver.resolve(classification, ticket_description)
final_result = supervisor.supervise(classification, routing, resolution)
```

### 5.2 Inter-Agent Data Contracts

**Classifier → Router:**
```json
{
  "category": "Hardware",
  "subcategory": "Printer",
  "confidence_score": 0.85,
  "all_scores": {"Hardware": 3, "Software": 0, ...},
  "reasoning": "Classified as Hardware based on keyword analysis"
}
```

**Router → Resolver:**
```json
{
  "department": "Hardware Support",
  "team": "IT Operations",
  "priority": "High",
  "sla_hours": 24,
  "assigned_to": "IT Operations",
  "reasoning": "Routed to Hardware Support with High priority"
}
```

**Resolver → Supervisor:**
```json
{
  "resolution_steps": ["Step 1...", "Step 2...", ...],
  "estimated_resolution_time": "4-24 hours",
  "references": ["KB Article...", ...],
  "knowledge_base_link": "kb/hardware.html",
  "reasoning": "Generated 5 resolution steps for Hardware issue"
}
```

---

## 6. Technology Stack Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         RUNTIME                              │
│                      Python 3.9+                             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   UI Layer   │    │  AI Layer    │    │  Data Layer   │
│              │    │              │    │              │
│ Streamlit    │    │ CrewAI       │    │ ChromaDB     │
│ 1.28.0       │    │ 0.1.0        │    │ 0.4.0        │
│              │    │              │    │              │
│              │    │ LangChain    │    │ FAISS        │
│              │    │ 0.1.0        │    │ 1.7.4        │
│              │    │              │    │              │
│              │    │ Google Gemini│    │ Pandas       │
│              │    │ gemini-1.5   │    │ 2.1.0        │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 6.1 Dependency Matrix

| Layer | Technology | Version | Purpose | License |
|-------|-----------|---------|---------|---------|
| UI | Streamlit | 1.28.0 | Web interface | Apache 2.0 |
| Orchestration | CrewAI | 0.1.0 | Agent framework | MIT |
| AI | LangChain | 0.1.0 | LLM integration | MIT |
| AI | langchain-google-genai | 0.0.1 | Gemini connector | MIT |
| Vector DB | ChromaDB | 0.4.0 | Vector storage | Apache 2.0 |
| Vector DB | FAISS | 1.7.4 | Vector search | MIT |
| Data | Pandas | 2.1.0 | Data manipulation | BSD |
| Data | NumPy | 1.24.0 | Numerical computing | BSD |
| Validation | Pydantic | 2.4.0 | Data validation | MIT |
| Config | python-dotenv | 1.0.0 | Environment variables | BSD |

---

## 7. Configuration Architecture

### 7.1 Environment Configuration (.env)

```
# LLM Configuration
GOOGLE_API_KEY=<api_key>
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7

# System Configuration
CONFIDENCE_THRESHOLD=0.75
ESCALATION_ENABLED=true
MAX_RESOLUTION_STEPS=10

# Vector Database
VECTOR_DB_TYPE=chromadb
VECTOR_DB_PATH=./data/knowledge_base

# Categories & Departments
TICKET_CATEGORIES=Hardware,Software,Network,Security,HR/IT Access,Other
DEPARTMENTS=Hardware Support,DevOps,Network Team,Security Team,IT Helpdesk
```

### 7.2 Configuration Flow

```
.env file
    │
    ▼
python-dotenv
    │
    ▼
Agent Configuration
    │
    ├─── ClassifierAgent (categories, keywords)
    ├─── RouterAgent (routing map, priority levels)
    ├─── ResolverAgent (resolution map, references)
    └─── SupervisorAgent (confidence threshold, escalation rules)
```

---

## 8. Security Architecture

### 8.1 Security Considerations

| Area | Concern | Mitigation |
|------|---------|------------|
| API Keys | Exposed credentials | Stored in .env, gitignored |
| Ticket Data | Sensitive information | Data anonymization in utils |
| LLM Input | Prompt injection | Input sanitization |
| Escalation | Security tickets | Forced escalation for Security category |
| Access Control | Unauthorized access | Future: Authentication layer |

### 8.2 Security Ticket Handling

```
Security Category Detected
        │
        ▼
┌──────────────────────────────┐
│  Forced Escalation           │
│  - Bypass auto-resolution    │
│  - Alert Security Team       │
│  - Log incident              │
└──────────────────────────────┘
```

---

## 9. Scalability Architecture

### 9.1 Horizontal Scaling Considerations

- **Agent Workers:** Each agent can be deployed as a separate microservice
- **Vector Database:** ChromaDB/FAISS can be scaled independently
- **LLM API:** Google Gemini API handles scaling on the cloud side
- **Caching:** Future implementation of response caching for common tickets

### 9.2 Future Architecture (Microservices)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│Classifier│    │ Router   │    │ Resolver │    │Supervisor│
│ Service  │───▶│ Service  │───▶│ Service  │───▶│ Service  │
│ (FastAPI)│    │(FastAPI) │    │(FastAPI) │    │(FastAPI) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
      │                │                │                │
      └────────────────┼────────────────┼────────────────┘
                       │                │
                       ▼                ▼
                ┌──────────────────────────────┐
                │    Message Queue (Future)    │
                │    RabbitMQ / Kafka          │
                └──────────────────────────────┘
```

---

## 10. Deployment Architecture

### 10.1 Current Deployment (Development)

```
Local Machine
├── Streamlit Server (localhost:8501)
├── Python Backend (in-process)
├── ChromaDB (local filesystem)
└── .env configuration
```

### 10.2 Future Production Deployment

```
Cloud Infrastructure (Future)
├── Load Balancer
│   └── Streamlit Application (scaled)
│       └── Agent Backend (FastAPI)
│           ├── Classifier Service
│           ├── Router Service
│           ├── Resolver Service
│           └── Supervisor Service
├── Vector Database (managed ChromaDB)
├── LLM API (Google Gemini Cloud)
└── Monitoring & Logging (Future)
```

---

## 11. Integration Architecture

### 11.1 External System Integration (Future)

| System | Integration Type | Purpose |
|--------|----------------|---------|
| ServiceNow | REST API | Ticket ingestion |
| Jira | REST API | Ticket tracking |
| Slack | Webhook | Notifications |
| Email | IMAP/SMTP | Ticket submission |
| LDAP/Active Directory | LDAP | User authentication |

### 11.2 API Endpoints (Future - FastAPI)

```
POST /api/tickets/submit       - Submit new ticket
GET  /api/tickets/{id}         - Get ticket status
POST /api/tickets/{id}/escalate - Manual escalation
GET  /api/agents/status        - Agent health check
GET  /api/metrics              - System metrics
```

---

## 12. Monitoring & Observability (Future)

### 12.1 Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Classification Accuracy | Correct category prediction | > 85% |
| Routing Accuracy | Correct department assignment | > 90% |
| Resolution Success Rate | Tickets resolved automatically | > 70% |
| Escalation Rate | Tickets requiring human review | < 30% |
| Processing Time | End-to-end ticket processing | < 5 seconds |
| Confidence Score Avg | Average confidence across tickets | > 0.80 |

---

## 13. Conclusion

The architecture follows a modular, agent-based approach that enables:
- Clear separation of concerns between agents
- Easy addition of new agents or capabilities
- Scalable deployment options
- Explainable AI decisions through per-agent reasoning
- Human-in-the-loop for quality assurance

The system is designed to evolve from the current rule-based implementation to a fully LLM-powered solution with RAG-based knowledge retrieval.
