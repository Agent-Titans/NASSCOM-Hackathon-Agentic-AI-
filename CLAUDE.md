# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-1.5-pro
CONFIDENCE_THRESHOLD=0.75
```

### Running the Application
```bash
streamlit run app.py
```
The UI will open at `http://localhost:8501`

### Testing Individual Agents
Each agent can be tested independently:
```python
# Example for testing classifier
from Agents.classifier import ClassifierAgent
classifier = ClassifierAgent()
result = classifier.classify("My printer is not working")
print(result)
```

## Code Architecture

### Multi-Agent Workflow
The system follows a sequential agent collaboration pattern:
1. **Classifier Agent** (`Agents/classifier.py`): Categorizes tickets (Hardware, Software, Network, Security, HR/IT Access)
2. **Router Agent** (`Agents/router.py`): Assigns department and priority (Low/Medium/High)
3. **Resolver Agent** (`Agents/resolver.py`): Generates step-by-step resolutions using RAG
4. **Supervisor Agent** (`Agents/supervisor.py`): Calculates confidence score and escalation decision

Data flow: Ticket Input → Classifier → Router → Resolver → Supervisor → Output

### System Layers
- **Layer 1**: Streamlit UI for ticket submission and result visualization
- **Layer 2**: Python + CrewAI backend orchestration
- **Layer 3**: LLM Intelligence (Google Gemini / GPT)
- **Layer 4**: RAG + Vector Database (ChromaDB/FAISS) for past ticket retrieval
- **Layer 5**: Decision & Policy Layer for confidence scoring and escalation rules

### Project Structure
```
.
├── app.py                      # Streamlit UI application (referenced in docs)
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
└── README.md                   # Project overview
```

### Key Components
- **Agents**: Built using CrewAI framework, each with a single responsibility
- **Knowledge Base**: Uses ChromaDB for vector storage and similarity search
- **Configuration**: Managed via `.env` file and `utils/config.py`
- **Data Processing**: Ticket preprocessing handled in `utils/data_processor.py`

### Communication Pattern
Agents communicate through dictionary outputs:
- Classifier → Router: Passes classification results
- Classifier/Router → Resolver: Provides category/subcategory for resolution
- All agents → Supervisor: Provides inputs for final confidence assessment

### Extending the System
- Add new categories: Update `ClassifierAgent.CATEGORIES` and corresponding mappings in Router/Resolver
- Modify routing logic: Update `RouterAgent.ROUTING_MAP` and priority calculation
- Enhance resolutions: Add to `ResolverAgent.RESOLUTIONS` dictionary
- Adjust confidence/threshhold: Modify `SupervisorAgent._calculate_confidence()` and thresholds