# Architecture Diagram - Visual Guide

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│  (Opens http://localhost:3000)                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP Requests
                            │ (GET, POST)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  React Components (page.tsx)                               │ │
│  │  - User types query                                        │ │
│  │  - Clicks "Research" button                                 │ │
│  │  - Displays results                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  State Management (useState)                              │ │
│  │  - query: string                                          │ │
│  │  - isLoading: boolean                                      │ │
│  │  - jobStatus: JobStatus                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  API Client (Axios)                                      │ │
│  │  - POST /api/research → Create job                        │ │
│  │  - GET /api/jobs/{id} → Poll status                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ REST API Calls
                            │ (JSON over HTTP)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  API Endpoints (api/main.py)                              │ │
│  │  POST /api/research                                       │ │
│  │  GET  /api/jobs/{job_id}                                  │ │
│  │  GET  /api/export/{job_id}                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Request Validation (Pydantic)                            │ │
│  │  - Validates incoming data                                │ │
│  │  - Type checking                                          │ │
│  │  - Error handling                                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Background Tasks                                         │ │
│  │  - Creates job with UUID                                 │ │
│  │  - Runs research in background                            │ │
│  │  - Updates job status                                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Function Calls
                            │ (Python)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              YOUR ORIGINAL CODE (Unchanged!)                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  LangGraph Orchestration (orchestration/graph.py)        │ │
│  │  - Supervisor Agent                                       │ │
│  │  - Research Agent                                         │ │
│  │  - Memory Agent                                          │ │
│  │  - Analyst Agent                                        │ │
│  │  - Summarizer Agent                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Tools                                                    │ │
│  │  - fetch_web.py (DuckDuckGo search)                     │ │
│  │  - call_llm.py (Gemini API)                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Memory Systems                                          │ │
│  │  - vector_memory.py (FAISS)                              │ │
│  │  - graph_memory.py (NetworkX)                             │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow (Step by Step)

### 1. User Starts Research

```
User Types: "AI in healthcare"
     │
     ▼
Frontend: startResearch() function
     │
     ├─> Sets isLoading = true
     ├─> Clears previous errors
     │
     ▼
POST /api/research
Body: { query: "AI in healthcare", n_results: 20 }
     │
     ▼
Backend: create_research() endpoint
     │
     ├─> Validates request (Pydantic)
     ├─> Generates UUID: "abc-123-def"
     ├─> Creates job: { status: "queued", ... }
     ├─> Starts background task
     │
     ▼
Returns: { job_id: "abc-123-def", status: "queued" }
     │
     ▼
Frontend: Receives job_id
     │
     ├─> Sets jobId = "abc-123-def"
     ├─> Starts polling: pollJobStatus("abc-123-def")
```

### 2. Background Processing

```
Background Task: run_research_job()
     │
     ├─> Updates: status = "processing"
     │
     ▼
Calls: graph.invoke({ query: "AI in healthcare", ... })
     │
     ▼
LangGraph Execution:
     │
     ├─> Supervisor → Research Agent
     │   └─> Searches DuckDuckGo
     │   └─> Fetches 20 URLs
     │
     ├─> Research → Memory Agent
     │   └─> Chunks text
     │   └─> Stores in FAISS
     │
     ├─> Memory → Analyst Agent
     │   └─> Searches vector memory
     │   └─> Finds relevant chunks
     │
     ├─> Analyst → Supervisor
     │   └─> Decision: "ready" or "need_more_info"
     │
     ├─> Supervisor → Summarizer
     │   └─> Calls Gemini API
     │   └─> Generates research topics
     │
     ▼
Result: { final_context: "Research areas:\n1. ...\n2. ..." }
     │
     ├─> Updates job: status = "completed"
     ├─> Stores: result, sources, citations
```

### 3. Frontend Polling

```
Frontend: pollJobStatus() runs every 2 seconds
     │
     ▼
GET /api/jobs/abc-123-def
     │
     ▼
Backend: Returns current job status
     │
     ├─> First call: { status: "processing", progress: "..." }
     ├─> Second call: { status: "processing", progress: "..." }
     ├─> Third call: { status: "completed", result: "..." }
     │
     ▼
Frontend: Receives status
     │
     ├─> Updates jobStatus state
     ├─> If completed:
     │   ├─> Sets isLoading = false
     │   ├─> Stops polling
     │   └─> Displays results
```

## Data Flow

```
┌──────────────┐
│ User Input   │
│ "AI in..."   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     POST /api/research
│  Frontend    │ ──────────────────────┐
│  State       │                         │
└──────┬───────┘                         │
       │                                 │
       │ Polling                         │
       │ GET /api/jobs/{id}             │
       │                                 │
       ▼                                 ▼
┌──────────────┐     ┌──────────────────┐
│  Display     │     │   Backend        │
│  Results     │◄────│   Job Store      │
└──────────────┘     └──────────────────┘
                            │
                            │ Background Task
                            ▼
                    ┌──────────────────┐
                    │  LangGraph       │
                    │  (Your Code)     │
                    └──────────────────┘
                            │
                            │ Results
                            ▼
                    ┌──────────────────┐
                    │  Job Store        │
                    │  (Updated)       │
                    └──────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────┐
│         React Component Tree            │
│                                          │
│  Home Component (page.tsx)               │
│  ├─ State: query, isLoading, jobStatus   │
│  ├─ Functions:                          │
│  │  ├─ startResearch()                  │
│  │  ├─ pollJobStatus()                  │
│  │  ├─ copyToClipboard()                │
│  │  └─ downloadResults()                │
│  └─ JSX:                                │
│     ├─ Input field                      │
│     ├─ Search button                    │
│     ├─ Progress indicator               │
│     ├─ Results display                  │
│     └─ Sources list                     │
└─────────────────────────────────────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────┐
│         Environment Variables           │
│  (.env file or system env)              │
│                                          │
│  GEMINI_API_KEY=xxx                     │
│  N_RESULTS=20                            │
│  PORT=8000                               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         config.py                       │
│                                          │
│  class Config:                           │
│    GEMINI_API_KEY = os.getenv(...)       │
│    N_RESULTS = int(os.getenv(...))       │
│    ...                                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Used Throughout App             │
│                                          │
│  from config import Config               │
│  api_key = Config.GEMINI_API_KEY         │
│  n_results = Config.N_RESULTS            │
└──────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────┐
│         Error Occurs                    │
│  (e.g., API key missing)                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Try/Except Block                │
│                                          │
│  try:                                    │
│    result = call_llm(prompt)            │
│  except Exception as e:                  │
│    logger.error(f"Error: {e}")          │
│    raise                                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Logging System                  │
│                                          │
│  - Logs to console                      │
│  - Logs to file (optional)              │
│  - Includes timestamp, level, message    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         User-Friendly Error             │
│                                          │
│  Frontend displays:                      │
│  "Error: Failed to start research"      │
│                                          │
│  Backend returns:                       │
│  { error: "GEMINI_API_KEY not set" }    │
└──────────────────────────────────────────┘
```

## Key Takeaways

1. **Separation:** Frontend and Backend are separate
2. **Communication:** HTTP REST API connects them
3. **Async:** Long tasks run in background
4. **State:** Frontend manages UI state
5. **Polling:** Frontend checks job status repeatedly
6. **Your Code:** Unchanged, just wrapped in API
