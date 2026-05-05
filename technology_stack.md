# Technology Stack Document - IT Ticket Routing & Automated Resolution System
**Team:** Agent Titans
**Event:** NASSCOM Agentic AI Hackathon 2026
**Version:** 1.0
**Date:** May 2026

---

## 1. Overview
This document lists all technologies, frameworks, libraries, and tools used in the IT Ticket Routing & Automated Resolution System, organized by system layer with versioning, purpose, and licensing details.

---

## 2. Runtime Environment
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| Python | 3.9+ | Core runtime for all backend components | PSF License |

---

## 3. Layer-Wise Technology Stack

### 3.1 Presentation Layer (UI)
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| Streamlit | 1.28.0 | Web interface for ticket submission and results visualization | Apache 2.0 |

### 3.2 Orchestration Layer
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| CrewAI | 0.1.0 | Multi-agent workflow coordination and sequential execution | MIT |
| Python-dotenv | 1.0.0 | Environment variable management from `.env` files | BSD |

### 3.3 Agent Intelligence Layer
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| LangChain | 0.1.0 | LLM integration and prompt management | MIT |
| langchain-google-genai | 0.0.1 | Google Gemini API connector for LangChain | MIT |
| Google Gemini API | gemini-1.5-pro | Large Language Model for AI-driven agent decisions | Proprietary (Google) |
| Pydantic | 2.4.0 | Data validation for agent inputs/outputs | MIT |
| pydantic-settings | Latest | Configuration management with `.env` integration | MIT |

### 3.4 Knowledge Layer (RAG + Vector Storage)
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| ChromaDB | 0.4.0 | Primary vector database for ticket embeddings and KB storage | Apache 2.0 |
| FAISS | 1.7.4 | Alternative vector database for similarity search | MIT |
| Sentence Transformers | Latest | Text embedding generation for vector storage | Apache 2.0 |

### 3.5 Data Layer
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| Pandas | 2.1.0 | Structured data manipulation and ticket batch processing | BSD |
| NumPy | 1.24.0 | Numerical computing for confidence scoring and metrics | BSD |

### 3.6 Future Expansion (Planned)
| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| FastAPI | Latest | REST API backend for microservice deployment | MIT |
| RabbitMQ/Kafka | Latest | Message queue for asynchronous ticket processing | MPL 2.0 / Apache 2.0 |
| ServiceNow API | N/A | ITSM integration for ticket ingestion | Proprietary |
| Jira API | N/A | Ticket tracking integration | Proprietary |
| Slack Webhook | N/A | Escalation and status notifications | Proprietary |

---

## 4. Complete Dependency Matrix
Consolidated from Architecture Document Section 6.1.

| Layer | Technology | Version | Purpose | License |
|-------|-----------|---------|---------|---------|
| Runtime | Python | 3.9+ | Core runtime | PSF License |
| UI | Streamlit | 1.28.0 | Web interface | Apache 2.0 |
| Orchestration | CrewAI | 0.1.0 | Agent framework | MIT |
| AI | LangChain | 0.1.0 | LLM integration | MIT |
| AI | langchain-google-genai | 0.0.1 | Gemini connector | MIT |
| AI | Google Gemini | gemini-1.5-pro | LLM for agents | Proprietary |
| Vector DB | ChromaDB | 0.4.0 | Vector storage | Apache 2.0 |
| Vector DB | FAISS | 1.7.4 | Vector search | MIT |
| Data | Pandas | 2.1.0 | Data manipulation | BSD |
| Data | NumPy | 1.24.0 | Numerical computing | BSD |
| Validation | Pydantic | 2.4.0 | Data validation | MIT |
| Config | python-dotenv | 1.0.0 | Environment variables | BSD |
| Config | pydantic-settings | Latest | Config management | MIT |
| Embeddings | Sentence Transformers | Latest | Text embeddings | Apache 2.0 |

---

## 5. Technology Stack Architecture Diagram
From Architecture Document Section 6.

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
│              │    │              │    │              │
│              │    │ Pydantic     │    │ NumPy        │
│              │    │ 2.4.0        │    │ 1.24.0       │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 6. Configuration Management
All configurable parameters are stored in `.env` (loaded via `python-dotenv` and `pydantic-settings`):

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `GOOGLE_API_KEY` | N/A | Google Gemini API authentication |
| `LLM_MODEL` | gemini-1.5-pro | LLM model selection |
| `LLM_TEMPERATURE` | 0.7 | LLM response randomness |
| `CONFIDENCE_THRESHOLD` | 0.75 | Minimum confidence for auto-resolution |
| `ESCALATION_ENABLED` | true | Toggle escalation logic |
| `MAX_RESOLUTION_STEPS` | 10 | Maximum resolution steps per ticket |
| `VECTOR_DB_TYPE` | chromadb | Vector database selection |
| `VECTOR_DB_PATH` | ./data/knowledge_base | Vector DB storage path |
| `TICKET_CATEGORIES` | Hardware,Software,Network,Security,HR/IT Access,Other | Valid ticket categories |
| `DEPARTMENTS` | Hardware Support,DevOps,Network Team,Security Team,IT Helpdesk | Valid routing departments |

---

## 7. License Summary
| License | Technologies |
|---------|---------------|
| MIT | CrewAI, LangChain, langchain-google-genai, Pydantic, pydantic-settings, FastAPI (future) |
| Apache 2.0 | Streamlit, ChromaDB, Sentence Transformers |
| BSD | Pandas, NumPy, python-dotenv |
| PSF License | Python |
| Proprietary | Google Gemini API, ServiceNow/Jira/Slack APIs (future) |
