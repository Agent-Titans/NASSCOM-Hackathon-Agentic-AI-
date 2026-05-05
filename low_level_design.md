# Low-Level Design Document (LLD)
# IT Ticket Routing & Automated Resolution System

**Team:** Agent Titans  
**Event:** NASSCOM Agentic AI Hackathon 2026  
**Version:** 1.0  
**Date:** May 2026  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Class Diagram](#2-class-diagram)
3. [Agent Designs](#3-agent-designs)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [Sequence Diagrams](#5-sequence-diagrams)
6. [State Transition Diagram](#6-state-transition-diagram)
7. [Database Design](#7-database-design)
8. [API Design](#8-api-design)
9. [Error Handling](#9-error-handling)
10. [Test Cases](#10-test-cases)

---

## 1. Introduction

### 1.1 Purpose

This Low-Level Design (LLD) document provides detailed implementation specifications for the IT Ticket Routing & Automated Resolution System. It covers class designs, method signatures, data structures, algorithms, and interaction patterns.

### 1.2 Scope

This document covers:
- Detailed class diagrams for all agents
- Method-level specifications
- Data models and structures
- Inter-agent communication protocols
- Database schema design
- API endpoint specifications
- Error handling strategies

---

## 2. Class Diagram

### 2.1 System Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           <<interface>>                         │
│                           Agent                                 │
├─────────────────────────────────────────────────────────────────┤
│ + process(ticket: Ticket) -> Dict[str, Any]                    │
│ + get_agent_name() -> str                                      │
│ + get_agent_type() -> str                                      │
└─────────────────────────────────────────────────────────────────┘
                                    △
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────┴───────┐         ┌───────┴───────┐         ┌───────┴───────┐
│  Classifier    │         │    Router      │         │   Resolver     │
│    Agent       │         │    Agent       │         │    Agent       │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ - CATEGORIES  │         │ - ROUTING_MAP │         │ - RESOLUTIONS  │
│ - keywords    │         │ - PRIORITIES  │         │ - steps       │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ + classify()  │         │ + route()     │         │ + resolve()    │
│ + _get_subcat()│        │ + _calc_prio()│         │ + _get_steps()│
└───────────────┘         └───────────────┘         └───────┬───────┘
                                                        │
                                                        │
                                                ┌───────┴───────┐
                                                │  Supervisor    │
                                                │    Agent       │
                                                ├───────────────┤
                                                │ - threshold   │
                                                │ - factors     │
                                                ├───────────────┤
                                                │ + supervise() │
                                                │ + _calc_conf()│
                                                │ + _determine_escalate()│
                                                └───────────────┘
```

### 2.2 Ticket Data Class

```
┌──────────────────────────────────────────────────────────────┐
│                        Ticket                                │
├──────────────────────────────────────────────────────────────┤
│ - ticket_id: str                                            │
│ - description: str                                          │
│ - urgency: str                                              │
│ - timestamp: datetime                                        │
│ - classification: Dict[str, Any]                            │
│ - routing: Dict[str, Any]                                    │
│ - resolution: Dict[str, Any]                                 │
│ - supervision: Dict[str, Any]                                │
├──────────────────────────────────────────────────────────────┤
│ + to_dict() -> Dict                                         │
│ + from_dict(data: Dict) -> Ticket                           │
│ + get_category() -> str                                     │
│ + get_priority() -> str                                     │
│ + needs_escalation() -> bool                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Agent Designs

### 3.1 ClassifierAgent

#### 3.1.1 Class Definition

```python
class ClassifierAgent:
    """
    Agent responsible for ticket classification.
    Analyzes ticket description and assigns category and subcategory.
    """
    
    CATEGORIES = {
        "Hardware": ["printer", "monitor", "keyboard", "mouse", "server", "hardware"],
        "Software": ["bug", "crash", "error", "install", "application", "software"],
        "Network": ["internet", "connection", "wifi", "vpn", "network"],
        "Security": ["password", "access", "permission", "breach", "security"],
        "HR/IT Access": ["account", "reset", "onboarding", "user", "email"],
    }
    
    SUBCATEGORIES = {
        "Hardware": ["Printer", "Monitor", "Server", "Peripheral"],
        "Software": ["Application", "OS", "Database", "License"],
        "Network": ["Connectivity", "VPN", "Bandwidth", "WiFi"],
        "Security": ["Access Control", "Authentication", "Data Breach"],
        "HR/IT Access": ["Account Reset", "Onboarding", "Permissions"],
    }
```

#### 3.1.2 Method Specifications

**Method: classify(ticket_description: str) -> Dict[str, Any]**

| Parameter | Type | Description |
|-----------|------|-------------|
| ticket_description | str | The ticket text to classify |

**Returns:**
```python
{
    "category": str,           # Primary category (Hardware, Software, etc.)
    "subcategory": str,        # Subcategory (Printer, Monitor, etc.)
    "confidence_score": float, # 0.0 to 1.0
    "all_scores": dict,        # Scores for all categories
    "reasoning": str           # Explanation of classification
}
```

**Algorithm:**
```
1. Convert ticket_description to lowercase
2. Initialize scores dictionary with all categories set to 0
3. For each category and its keywords:
   a. Count keyword occurrences in ticket_description
   b. Store count in scores[category]
4. Find category with maximum score
5. If max score is 0, set category to "Other"
6. Determine subcategory based on primary category
7. Calculate confidence = min(score / 3, 1.0)
8. Return classification dictionary
```

**Time Complexity:** O(n * m) where n = number of categories, m = average keywords per category

---

### 3.2 RouterAgent

#### 3.2.1 Class Definition

```python
class RouterAgent:
    """
    Agent responsible for routing tickets to appropriate departments.
    Determines department, team, priority, and SLA.
    """
    
    ROUTING_MAP = {
        "Hardware": {
            "department": "Hardware Support",
            "team": "IT Operations",
            "sla_hours": 24
        },
        "Software": {
            "department": "DevOps",
            "team": "Application Support",
            "sla_hours": 8
        },
        "Network": {
            "department": "Network Team",
            "team": "Infrastructure",
            "sla_hours": 4
        },
        "Security": {
            "department": "Security Team",
            "team": "Information Security",
            "sla_hours": 2
        },
        "HR/IT Access": {
            "department": "IT Helpdesk",
            "team": "Identity Management",
            "sla_hours": 2
        },
    }
    
    PRIORITY_LEVELS = {
        "Critical": {"value": 4, "multiplier": 0.5},
        "High": {"value": 3, "multiplier": 0.75},
        "Medium": {"value": 2, "multiplier": 1.0},
        "Low": {"value": 1, "multiplier": 1.5},
    }
```

#### 3.2.2 Method Specifications

**Method: route(classification: Dict[str, Any], urgency: str) -> Dict[str, Any]**

| Parameter | Type | Description |
|-----------|------|-------------|
| classification | Dict | Output from ClassifierAgent |
| urgency | str | User-perceived urgency (Low/Medium/High/Critical) |

**Returns:**
```python
{
    "department": str,      # Target department
    "team": str,            # Specific team
    "priority": str,        # Priority level
    "sla_hours": int,       # SLA in hours
    "assigned_to": str,     # Assigned team
    "reasoning": str        # Explanation of routing decision
}
```

**Algorithm:**
```
1. Extract category from classification dictionary
2. Look up category in ROUTING_MAP
3. If category not found, use default (Hardware Support)
4. Extract urgency level from input
5. Calculate priority based on:
   a. Base priority from urgency
   b. Category-specific adjustments (Security → raise priority)
   c. Confidence score influence
6. Return routing dictionary
```

---

### 3.3 ResolverAgent

#### 3.3.1 Class Definition

```python
class ResolverAgent:
    """
    Agent responsible for generating resolution steps.
    Uses knowledge base and RAG for context-aware suggestions.
    """
    
    RESOLUTIONS = {
        "Hardware": {
            "Printer": [
                "Check if printer is powered on",
                "Verify network connectivity to printer",
                "Clear printer queue on your computer",
                "Restart the printer device",
                "Update printer drivers",
            ],
            # ... more subcategories
        },
        "Software": { ... },
        "Network": { ... },
        "Security": { ... },
        "HR/IT Access": { ... },
    }
```

#### 3.3.2 Method Specifications

**Method: resolve(classification: Dict[str, Any], ticket_description: str) -> Dict[str, Any]**

| Parameter | Type | Description |
|-----------|------|-------------|
| classification | Dict | Output from ClassifierAgent |
| ticket_description | str | Original ticket description |

**Returns:**
```python
{
    "resolution_steps": List[str],    # Step-by-step instructions
    "estimated_resolution_time": str, # Expected resolution time
    "references": List[str],         # Knowledge base references
    "knowledge_base_link": str,      # Link to KB article
    "reasoning": str                 # Explanation of resolution
}
```

**Algorithm:**
```
1. Extract category and subcategory from classification
2. Look up resolution steps in RESOLUTIONS dictionary
3. If no steps found, return generic steps
4. Estimate resolution time based on category
5. Generate knowledge base references
6. Return resolution dictionary
```

---

### 3.4 SupervisorAgent

#### 3.4.1 Class Definition

```python
class SupervisorAgent:
    """
    Agent responsible for final review and confidence assessment.
    Determines if ticket should be escalated to human.
    """
    
    CONFIDENCE_THRESHOLD = 0.75
    ESCALATION_REASONS = {
        "LOW_CONFIDENCE": "Confidence below threshold",
        "SECURITY_ISSUE": "Security issue requires human review",
        "CRITICAL_PRIORITY": "Critical priority needs immediate attention",
        "NO_RESOLUTION": "No automated resolution available",
    }
```

#### 3.4.2 Method Specifications

**Method: supervise(classification: Dict, routing: Dict, resolution: Dict) -> Dict[str, Any]**

| Parameter | Type | Description |
|-----------|------|-------------|
| classification | Dict | Output from ClassifierAgent |
| routing | Dict | Output from RouterAgent |
| resolution | Dict | Output from ResolverAgent |

**Returns:**
```python
{
    "category": str,
    "subcategory": str,
    "department": str,
    "team": str,
    "priority": str,
    "confidence": float,
    "escalate": bool,
    "escalation_reason": str,
    "resolution_steps": List[str],
    "estimated_time": str,
    "sla_hours": int,
    "classifier_notes": str,
    "router_notes": str,
    "supervisor_notes": str,
    "similar_tickets": List[str],
    "processing_status": str,
    "requires_human_review": bool
}
```

**Algorithm:**
```
1. Calculate overall confidence:
   a. Get classifier confidence (weight: 40%)
   b. Get resolver confidence based on steps available (weight: 60%)
   c. Apply category-specific adjustments
   d. Return weighted average

2. Determine escalation:
   a. Check if Security category → escalate
   b. Check if confidence < threshold → escalate
   c. Check if no resolution steps → escalate
   d. Check if Critical priority → escalate

3. Generate supervisor notes

4. Compile and return final result dictionary
```

**Confidence Calculation Formula:**
```
overall_confidence = (classifier_confidence * 0.4) + (resolver_confidence * 0.6)

where:
- classifier_confidence = classification["confidence_score"]
- resolver_confidence = min(len(resolution_steps) / 5, 1.0)

Security adjustment:
- If category == "Security": resolver_confidence *= 0.8
```

---

## 4. Data Flow Diagrams

### 4.1 Level 0 DFD (Context Diagram)

```
                    ┌──────────────────┐
                    │   IT Support     │
                    │   Staff          │
                    └────────┬─────────┘
                             │ Ticket
                             │ Description
                             ▼
                    ┌──────────────────┐
                    │                  │
                    │  IT TICKET       │
             Result │  ROUTING         │ Escalation
         ◀──────── │  SYSTEM          │ ─────────▶
                    │                  │
                    └──────────────────┘
                             │
                             │ Resolution
                             │ Steps
                             ▼
                    ┌──────────────────┐
                    │   End User       │
                    │   (Ticket        │
                    │   Submitter)     │
                    └──────────────────┘
```

### 4.2 Level 1 DFD

```
                    ┌──────────────────┐
                    │  User /         │
                    │  IT Staff       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Streamlit UI    │
                    │  (Input Form)    │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │ Classifier  │    │   Router    │    │  Resolver   │
  │   Agent     │───▶│   Agent    │───▶│   Agent     │
  └─────────────┘    └─────────────┘    └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │ Supervisor   │
                                         │   Agent     │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │   Output    │
                                         │  (JSON)     │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  Streamlit   │
                                         │  UI (Result) │
                                         └─────────────┘
```

### 4.3 Data Store Diagram

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│   Ticket     │─────▶│  Agent      │─────▶│  Knowledge   │
│   Input      │      │  Processing │      │  Base        │
│              │      │              │      │  (ChromaDB)  │
└──────────────┘      └──────────────┘      └──────────────┘
         │                     │                      │
         │                     ▼                      │
         │              ┌──────────────┐            │
         │              │              │            │
         └─────────────▶│  Final       │◀───────────┘
                        │  Output      │
                        │              │
                        └──────────────┘
```

---

## 5. Sequence Diagrams

### 5.1 Main Ticket Processing Sequence

```
User       Streamlit    Classifier    Router    Resolver   Supervisor
 │            │            │            │          │           │
 │─Submit───▶│            │            │          │           │
 │  Ticket   │            │            │          │           │
 │            │─classify─▶│            │          │           │
 │            │            │─category─│          │           │
 │            │◀───────────│            │          │           │
 │            │            │            │          │           │
 │            │─route─────│───────────▶│          │           │
 │            │            │            │─dept     │           │
 │            │◀───────────│───────────│          │           │
 │            │            │            │          │           │
 │            │─resolve───│───────────│─────────▶│           │
 │            │            │            │          │─steps     │
 │            │◀───────────│───────────│──────────│           │
 │            │            │            │          │           │
 │            │─supervise─│───────────│──────────│──────────▶│
 │            │            │            │          │           │
 │            │            │            │          │─result    │
 │◀─Display──│◀──────────│───────────│──────────│───────────│
 │            │            │            │          │           │
```

### 5.2 Escalation Decision Sequence

```
Supervisor       Confidence    Escalation
  Agent            Check         Logic
    │                │              │
    │─Calculate─────▶│              │
    │  Confidence    │              │
    │                │─Score < 75%? │
    │                │              │─Yes─────▶
    │                │              │         │
    │                │◀─────────────│         │
    │                │              │         │
    │◀───────────────│              │         │
    │  escalate=True│              │         │
    │  reason=Low   │              │         │
    │  confidence   │              │         │
    │                │              │         │
    │─Set───────────│              │         │
    │  requires_    │              │         │
    │  human_review │              │         │
    │                │              │         │
    │─Return───────▶│              │         │
    │  Final Result │              │         │
    │                │              │         │
```

---

## 6. State Transition Diagram

### 6.1 Ticket Lifecycle States

```
           ┌─────────────────────────┐
           │     TICKET CREATED       │
           │   (Initial State)       │
           └───────────┬─────────────┘
                       │
                       ▼
           ┌─────────────────────────┐
           │     CLASSIFYING          │
           │   (Agent 1 Processing)  │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     ROUTING              │
           │   (Agent 2 Processing)  │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     RESOLVING           │
           │   (Agent 3 Processing)  │
           └───────────┬─────────────┘
                       │ Success
                       ▼
           ┌─────────────────────────┐
           │     SUPERVISING         │
           │   (Agent 4 Processing) │
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
                                  │
                                  ▼
                          ┌─────────────────┐
                          │  CLOSED         │
                          │  (After Human)  │
                          └─────────────────┘
```

### 6.2 State Transition Table

| Current State | Event | Next State | Action |
|--------------|-------|------------|--------|
| CREATED | Submit ticket | CLASSIFYING | Initialize ClassifierAgent |
| CLASSIFYING | Classification complete | ROUTING | Pass to RouterAgent |
| CLASSIFYING | Classification failed | ERROR | Log error, escalate |
| ROUTING | Routing complete | RESOLVING | Pass to ResolverAgent |
| ROUTING | Routing failed | ERROR | Log error, escalate |
| RESOLVING | Resolution complete | SUPERVISING | Pass to SupervisorAgent |
| RESOLVING | No resolution | SUPERVISING | Continue with empty steps |
| SUPERVISING | Confidence >= threshold | RESOLVED | Auto-resolve ticket |
| SUPERVISING | Confidence < threshold | ESCALATED | Send to human review |
| ESCALATED | Human resolves | CLOSED | Mark ticket as closed |
| RESOLVED | Verified fixed | CLOSED | Mark ticket as closed |
| ERROR | Manual intervention | ROUTING | Restart from routing |

---

## 7. Database Design

### 7.1 Vector Database Schema (ChromaDB)

#### Collection: ticket_knowledge_base

| Field | Type | Description |
|-------|------|-------------|
| document | str | Ticket description text |
| embedding | list[float] | Vector embedding of document |
| metadata | dict | Additional ticket metadata |

**Metadata structure:**
```json
{
    "ticket_id": "T-2045",
    "category": "Hardware",
    "subcategory": "Printer",
    "department": "Hardware Support",
    "priority": "Medium",
    "resolution_steps": ["Step 1...", "Step 2..."],
    "resolution_time_hours": 2,
    "timestamp": "2026-05-01T10:30:00Z",
    "resolved": true
}
```

### 7.2 Sample Tickets Data Structure

```json
[
    {
        "ticket_id": "T-001",
        "description": "My printer is not printing. The queue shows documents waiting but nothing happens.",
        "urgency": "Medium",
        "category": "Hardware",
        "subcategory": "Printer",
        "department": "Hardware Support",
        "priority": "Medium",
        "resolution_steps": [
            "Check if printer is powered on",
            "Clear printer queue",
            "Restart printer"
        ],
        "confidence_score": 0.85,
        "escalate": false
    }
]
```

### 7.3 Entity Relationship Diagram

```
┌─────────────────────┐
│       TICKET         │
├─────────────────────┤
│ PK ticket_id        │
│    description      │
│    urgency          │
│    timestamp        │
│    status           │
└─────────┬───────────┘
          │
          │
          │    ┌─────────────────────┐
          │    │    CLASSIFICATION    │
          │    ├─────────────────────┤
          │    │ PK ticket_id (FK)   │
          │    │    category          │
          │    │    subcategory      │
          │    │    confidence_score │
          └───▶│    reasoning        │
               └─────────────────────┘
                        │
                        │
                        │    ┌─────────────────────┐
                        │    │       ROUTING        │
                        │    ├─────────────────────┤
                        │    │ PK ticket_id (FK)   │
                        │    │    department        │
                        │    │    team              │
                        │    │    priority          │
                        │    │    sla_hours         │
                        └───▶│    reasoning        │
                             └─────────────────────┘
                                      │
                                      │
                                      │    ┌─────────────────────┐
                                      │    │     RESOLUTION      │
                                      │    ├─────────────────────┤
                                      │    │ PK ticket_id (FK)   │
                                      │    │    steps            │
                                      │    │    estimated_time   │
                                      │    │    references      │
                                      └───▶│    kb_link         │
                                           └─────────────────────┘
```

---

## 8. API Design

### 8.1 Current Implementation (In-Process)

Currently, agents communicate via direct Python function calls:

```python
# app.py (Streamlit application)
def process_ticket(ticket_description: str, urgency: str) -> Dict[str, Any]:
    """Process a ticket through all agents."""
    
    # Initialize agents
    classifier = ClassifierAgent()
    router = RouterAgent()
    resolver = ResolverAgent()
    supervisor = SupervisorAgent()
    
    # Sequential processing
    classification = classifier.classify(ticket_description)
    routing = router.route(classification, urgency)
    resolution = resolver.resolve(classification, ticket_description)
    final_result = supervisor.supervise(classification, routing, resolution)
    
    return final_result
```

### 8.2 Future API Design (FastAPI)

#### 8.2.1 Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | /api/tickets | Submit new ticket | TicketRequest | TicketResponse |
| GET | /api/tickets/{id} | Get ticket status | - | TicketResponse |
| PUT | /api/tickets/{id} | Update ticket | TicketUpdate | TicketResponse |
| POST | /api/tickets/{id}/escalate | Escalate ticket | - | SuccessResponse |
| GET | /api/agents/health | Agent health check | - | HealthResponse |
| GET | /api/metrics | System metrics | - | MetricsResponse |

#### 8.2.2 Request/Response Schemas

**TicketRequest:**
```python
class TicketRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000)
    urgency: Literal["Low", "Medium", "High", "Critical"]
    submitted_by: Optional[str] = None
    attachments: Optional[List[str]] = None
```

**TicketResponse:**
```python
class TicketResponse(BaseModel):
    ticket_id: str
    category: str
    subcategory: str
    department: str
    priority: str
    confidence: float
    escalate: bool
    escalation_reason: Optional[str]
    resolution_steps: List[str]
    estimated_time: str
    sla_hours: int
    processing_status: str
    similar_tickets: List[str]
    created_at: datetime
```

**HealthResponse:**
```python
class HealthResponse(BaseModel):
    status: str  # "healthy" or "degraded"
    agents: Dict[str, str]  # {"classifier": "up", "router": "up", ...}
    version: str
    uptime_seconds: float
```

### 8.3 Future Message Queue Integration

For asynchronous processing:

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ Producer  │───▶│   RabbitMQ   │───▶│  Consumer    │
│ (Streamlit)│    │   Queue     │    │  (Agents)    │
└──────────┘    └──────────────┘    └──────────────┘
      │                                    │
      │                                    ▼
      │                            ┌──────────────┐
      │                            │  Result      │
      │                            │  Queue       │
      │                            └──────────────┘
      │                                    │
      ▼                                    ▼
┌──────────┐                       ┌──────────────┐
│  User    │◀──────────────────────│  WebSocket   │
│  UI      │                       │  Notification│
└──────────┘                       └──────────────┘
```

---

## 9. Error Handling

### 9.1 Error Categories

| Category | Examples | Handling Strategy |
|----------|---------|-------------------|
| Input Validation | Empty description, invalid urgency | Return 400 Bad Request |
| Agent Failure | LLM API error, timeout | Retry with exponential backoff |
| Data Not Found | Category not in map | Use default values |
| External Service | Vector DB unavailable | Fallback to keyword matching |
| Configuration | Missing API key | Fail fast with clear error |

### 9.2 Error Handling Flow

```python
def process_ticket_with_error_handling(ticket_description, urgency):
    try:
        # Validate input
        if not ticket_description or len(ticket_description.strip()) < 10:
            return {"error": "Invalid ticket description", "code": 400}
        
        # Process through agents
        classification = classifier.classify(ticket_description)
        
        # Check for classification failure
        if not classification.get("category"):
            return {"error": "Classification failed", "code": 500, "escalate": True}
        
        routing = router.route(classification, urgency)
        resolution = resolver.resolve(classification, ticket_description)
        final_result = supervisor.supervise(classification, routing, resolution)
        
        return final_result
        
    except Exception as e:
        # Log error
        logger.error(f"Ticket processing failed: {str(e)}")
        
        # Return error with escalation
        return {
            "error": str(e),
            "code": 500,
            "escalate": True,
            "escalation_reason": f"System error: {str(e)}"
        }
```

### 9.3 Retry Strategy

| Operation | Max Retries | Backoff | Fallback |
|-----------|-------------|---------|----------|
| LLM API Call | 3 | Exponential (1s, 2s, 4s) | Keyword-based classification |
| Vector DB Query | 2 | Fixed (1s) | Empty results |
| Agent Processing | 1 | None | Escalate to human |

---

## 10. Test Cases

### 10.1 Unit Tests

#### ClassifierAgent Tests

| Test Case ID | Input | Expected Output | Assertion |
|-------------|-------|-----------------|-----------|
| TC-CLS-001 | "My printer is not working" | category="Hardware", subcategory="Printer" | Verify category and subcategory |
| TC-CLS-002 | "I can't connect to VPN" | category="Network", subcategory="VPN" | Verify category and subcategory |
| TC-CLS-003 | "" (empty string) | category="Other" or default | Verify handles empty input |
| TC-CLS-004 | "a" * 1000 (very long) | Valid classification | Verify handles long input |
| TC-CLS-005 | "Something weird happened" | category with lowest score | Verify unknown category handling |

#### RouterAgent Tests

| Test Case ID | Input | Expected Output | Assertion |
|-------------|-------|-----------------|-----------|
| TC-RTE-001 | category="Hardware", urgency="High" | department="Hardware Support", priority="High" | Verify routing |
| TC-RTE-002 | category="Security", urgency="Low" | priority="High" (escalated) | Verify security elevation |
| TC-RTE-003 | category="Unknown", urgency="Medium" | Default routing | Verify fallback |

#### ResolverAgent Tests

| Test Case ID | Input | Expected Output | Assertion |
|-------------|-------|-----------------|-----------|
| TC-RES-001 | category="Hardware", subcategory="Printer" | 5 resolution steps | Verify steps returned |
| TC-RES-002 | category="Unknown", subcategory="Unknown" | Generic steps | Verify fallback |
| TC-RES-003 | category="Security", subcategory="Access Control" | Steps with security notes | Verify category-specific |

#### SupervisorAgent Tests

| Test Case ID | Input | Expected Output | Assertion |
|-------------|-------|-----------------|-----------|
| TC-SUP-001 | confidence=0.85, category="Hardware" | escalate=False | Verify high confidence |
| TC-SUP-002 | confidence=0.60, category="Software" | escalate=True, reason contains "confidence" | Verify low confidence escalation |
| TC-SUP-003 | confidence=0.90, category="Security" | escalate=True, reason contains "Security" | Verify security escalation |
| TC-SUP-004 | confidence=0.90, priority="Critical" | escalate=True, reason contains "Critical" | Verify critical escalation |

### 10.2 Integration Tests

| Test Case ID | Scenario | Steps | Expected Result |
|-------------|----------|-------|-----------------|
| TC-INT-001 | Full pipeline - Hardware ticket | Submit "Printer not working", urgency="Medium" | Complete result with category, routing, resolution, no escalation |
| TC-INT-002 | Full pipeline - Security ticket | Submit "Possible data breach", urgency="Critical" | Complete result with escalation=True |
| TC-INT-003 | Full pipeline - Low confidence | Submit vague description | Complete result with escalation=True, reason="Low confidence" |

### 10.3 Performance Tests

| Test Case ID | Scenario | Metric | Target |
|-------------|----------|--------|--------|
| TC-PERF-001 | Process 100 tickets sequentially | Average processing time | < 5 seconds per ticket |
| TC-PERF-002 | Process single ticket | End-to-end latency | < 3 seconds |
| TC-PERF-003 | Agent processing | Classifier time | < 0.5 seconds |
| TC-PERF-004 | Agent processing | Router time | < 0.5 seconds |
| TC-PERF-005 | Agent processing | Resolver time | < 1 second |

---

## 11. Configuration Management

### 11.1 Configuration Parameters

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    google_api_key: str
    llm_model: str = "gemini-1.5-pro"
    llm_temperature: float = 0.7
    
    # System Configuration
    confidence_threshold: float = 0.75
    escalation_enabled: bool = True
    max_resolution_steps: int = 10
    
    # Vector Database
    vector_db_type: str = "chromadb"
    vector_db_path: str = "./data/knowledge_base"
    
    # Categories
    ticket_categories: List[str] = [
        "Hardware", "Software", "Network", 
        "Security", "HR/IT Access", "Other"
    ]
    
    # Departments
    departments: List[str] = [
        "Hardware Support", "DevOps", "Network Team",
        "Security Team", "IT Helpdesk"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 12. Logging and Monitoring

### 12.1 Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed agent processing steps |
| INFO | Ticket processing start/end |
| WARNING | Low confidence, fallback to defaults |
| ERROR | Agent failures, API errors |
| CRITICAL | System failures, data corruption |

### 12.2 Log Format

```python
# Example log output
[2026-05-05 14:30:15] [INFO] [ClassifierAgent] Processing ticket T-2045
[2026-05-05 14:30:15] [DEBUG] [ClassifierAgent] Keywords found: printer(1), hardware(0)
[2026-05-05 14:30:15] [INFO] [ClassifierAgent] Classified as Hardware (confidence: 0.85)
[2026-05-05 14:30:16] [INFO] [RouterAgent] Routed to Hardware Support (priority: Medium)
[2026-05-05 14:30:16] [INFO] [ResolverAgent] Generated 5 resolution steps
[2026-05-05 14:30:17] [INFO] [SupervisorAgent] Confidence: 0.82, Escalate: No
[2026-05-05 14:30:17] [INFO] [System] Ticket T-2045 processed successfully
```

---

## 13. Future Enhancements

### 13.1 Short Term (1-3 months)
- Integration with Google Gemini API for LLM-based classification
- RAG implementation with ChromaDB
- FastAPI backend for REST API
- ServiceNow/Jira integration

### 13.2 Medium Term (3-6 months)
- Machine learning feedback loop
- Real-time ticket stream processing
- Advanced security escalation rules
- Multi-language support

### 13.3 Long Term (6+ months)
- Predictive analytics for ticket volume
- Auto-remediation (execute fixes automatically)
- Integration with ITSM tools
- Advanced reporting and dashboards

---

## 14. Conclusion

This LLD provides a comprehensive blueprint for implementing the IT Ticket Routing & Automated Resolution System. The modular agent-based architecture ensures maintainability, scalability, and explainability. Each agent has clearly defined responsibilities, inputs, and outputs, making the system easy to understand, test, and extend.

The design supports evolution from the current rule-based implementation to a fully LLM-powered solution with RAG-based knowledge retrieval, positioning the system for long-term success in production environments.
