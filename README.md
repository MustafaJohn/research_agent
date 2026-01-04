# Multi-Agent Research System (Execution-Centric Prototype)

This project implements an execution-driven, agentic research system using LangGraph. The focus is on **control flow, state management, tool isolation, and memory separation**, rather than prompt chaining. 

The system is intentionally designed as a **stateless execution graph** with explicit state transitions and failure boundaries.

---

## Architecture Overview

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
