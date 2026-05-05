# NASSCOM-Hackathon-Agentic-AI-
Note: Please read Tracking/Simplified_project_structure for a more simplified in-depth project doc

The repository will contain all files and entity diagrams of the IT ticketing Agentic AI system
# Intelligent Multi-Agent System for IT Ticket Routing and Automated Resolution

Team: Agent Titans | NASSCOM Agentic AI Hackathon 2026

## Overview
An autonomous, multi-agent AI solution for IT ticket classification, routing, automated resolution, and intelligent escalation. Uses sequential agent collaboration (Classifier → Router → Resolver → Supervisor) with RAG-based knowledge retrieval.

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
streamlit run app.py
```

The UI will open at `http://localhost:8501`

## Architecture

### Multi-Agent Workflow
1. **Classifier Agent**: Categorizes tickets (Hardware, Software, Network, Security, HR/IT Access, etc.)
2. **Router Agent**: Assigns department and priority (Low/Medium/High)
3. **Resolver Agent**: Generates step-by-step resolutions using RAG
4. **Supervisor Agent**: Calculates confidence score and escalation decision

```
Ticket Input → Classifier → Router → Resolver → Supervisor → Output
```

### System Layers
- **Layer 1**: Streamlit UI for ticket submission and result visualization
- **Layer 2**: Python + CrewAI backend orchestration
- **Layer 3**: LLM Intelligence (Google Gemini / GPT)
- **Layer 4**: RAG + Vector Database (ChromaDB/FAISS) for past ticket retrieval
- **Layer 5**: Decision & Policy Layer for confidence scoring and escalation rules

## Project Structure
```
.
├── app.py                      # Streamlit UI application
├── agents/
│   ├── __init__.py
│   ├── classifier.py           # Ticket classification agent
│   ├── router.py               # Department routing agent
│   ├── resolver.py             # Resolution suggestion agent
│   └── supervisor.py           # Confidence & escalation agent
├── knowledge/
│   ├── __init__.py
│   ├── rag_handler.py          # RAG retrieval logic
│   └── vector_store.py         # ChromaDB integration
├── utils/
│   ├── __init__.py
│   ├── data_processor.py       # Ticket preprocessing
│   └── config.py               # Configuration management
├── data/
│   ├── sample_tickets.json     # Sample ticket database
│   └── knowledge_base/         # Vector database storage
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Key Features
- **Automated Classification**: Categorizes tickets with high accuracy
- **Smart Routing**: Assigns correct departments with priority levels
- **RAG-based Resolution**: References past tickets for context-aware suggestions
- **Confidence Scoring**: Every decision includes a confidence percentage
- **Intelligent Escalation**: Low-confidence cases escalated to humans
- **Explainability**: Shows reasoning from each agent step

## Technology Stack
| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Agent Framework | CrewAI / LangChain |
| UI | Streamlit |
| LLM | Google Gemini / GPT-4o |
| Vector Database | ChromaDB |
| API Framework | FastAPI (future) |

## Environment Setup

Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-1.5-pro
CONFIDENCE_THRESHOLD=0.75
```

## Usage Example

1. **Submit a Ticket**: Enter ticket description in Streamlit UI
2. **Agents Process**: System runs through all 4 agents sequentially
3. **View Results**: See category, department, priority, resolution steps, confidence, and escalation recommendation

**Example Output:**
```
Category: Software
Department: DevOps Team
Priority: High
Confidence: 0.92
Resolution: 
  1. Check application logs
  2. Verify database connectivity
  3. Restart service
Escalation: No
```

## Evaluation Metrics
- **Accuracy**: Correct categorization rate
- **Routing Accuracy**: Correct department assignment rate
- **Escalation Rate**: Percentage of low-confidence escalations
- **Resolution Quality**: User satisfaction on suggested fixes


## Future Enhancements
- FastAPI middleware for ServiceNow/Jira integration
- Real-time ticket stream processing
- Machine learning feedback loop for continuous improvement
- Advanced security-specific escalation rules
- Multi-language support


## Team
Agent Titans - NASSCOM Agentic AI Hackathon 2026

