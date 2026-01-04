# Multi-Agent Research System 

This project implements an execution-driven, agentic research system using LangGraph. The focus is on **control flow, state management, tool isolation, and memory separation**, rather than prompt chaining. 

The system is intentionally designed as a stateless execution graph with explicit state transitions and defined failure boundaries.

---

## Architecture Overview
```
research_agent/
│
├── tools/        <- Agentic tools
│   ├── fetch_web.py
│   └── call_llm.py
│
├── memory/        <- Persistent Memory
│   ├── vector_memory.py
│   └── graph_memory.py
│   └── chunker.py
│
├── agents/        <- Agents 
│   ├── researcher.py
│   ├── memory_agent.py
│   ├── analyst.py
│   └── summarizer.py
│   └── memory_agent.py
│   └── context_builder.py
│
├── orchestration/
│   └── graph.py   <- LangGraph DAG
│   └── state.py
│
└── main.py        <- Entry Point
```
<img width="489" height="447" alt="image" src="https://github.com/user-attachments/assets/8706cd06-b394-4843-baf6-d186be9dace8" />

## Design Principles

- **Execution-first orchestration**
- **Explicit state passed between nodes**
- **Tool failures surfaced into state**
- **Supervisor-controlled decision flow**
- **Memory separated from execution**
- **LLMs treated as interchangeable components**

## State Model

All agents operate on a shared `ResearchState`:

```python
class ResearchState(TypedDict):
    query: str
    fetched_docs: list
    vector_results: list
    graph_results: List
    final_context: str
    next_step: str
    analysis_decision: str
    sources: Dict   
```
## Tools

### Web Fetching Tool
- Using DDGS tool to fetch URLs using DuckDuckGo's utility
- Parsing each URL using Beautiful Soup

### LLM
- Calling Gemimi using Gemini's API

## Memory Subsystems

### Vector Memory
- Used FAISS for storing into vector DB
- Used for semantic retrieval
- Info fetched from the internet is stored in vector memory
  
### Graph Memory
- Persistent entity co-occurrence graph
- Optimized for auditability and traceability
- Used networkx for creating the graph and using Spacy to create tokens
Note: Install Spacy's "en_core_web_trf" transformer using the steps below: 
```python
pip install spacy
python -m spacy download en_core_web_trf
```
## Failure Handling
- Tool calls are isolated per agent
- Failures do not crash the graph
- Supervisor node decides whether to continue or abort
- System supports deterministic re-runs
- LLM does not hallucinate random stuff when the memory retrieved is garbage, as it is grounded by some context and user query.

## Running the system
```python
python main.py
```
