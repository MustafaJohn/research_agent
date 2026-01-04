# Multi-Agent Research System 

This project implements an execution-driven, agentic research system using LangGraph. The focus is on **control flow, state management, tool isolation, and memory separation**, rather than prompt chaining. 

The system is intentionally designed as a **stateless execution graph** with explicit state transitions and failure boundaries.

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
│   └── .py
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
    graph_results: list
    final_context: str
    next_step: str
    analysis_decision: str
```

## Memory Subsystems

### Vector Memory
- Used for semantic retrieval
- Info fetched from the internet is stored in vector memory
  
### Graph Memory
- Persistent entity co-occurrence graph
- Optimized for auditability and traceability

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
