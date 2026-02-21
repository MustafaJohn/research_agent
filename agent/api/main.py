"""
FastAPI backend for the Research Agent web application.
"""
import os
import sys
import uuid
import asyncio
from typing import Dict, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from config import Config
from utils.logging_config import setup_logging
from orchestration.graph import build_graph

# Setup logging
setup_logging()
import logging
logger = logging.getLogger(__name__)

# Global state for job tracking
jobs: Dict[str, Dict] = {}
conversations: Dict[str, List[Dict]] = {}

# Initialize graph
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global graph
    Config.validate()
    Config.ensure_directories()
    graph = build_graph()
    logger.info("Research Agent API started")
    yield
    logger.info("Research Agent API shutting down")

app = FastAPI(
    title="Research Agent API",
    description="API for the Research Assistant Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ResearchRequest(BaseModel):
    query: str
    n_results: Optional[int] = None

class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    result: Optional[str] = None
    sources: Optional[list] = None
    citations: Optional[list] = None
    error: Optional[str] = None
    created_at: Optional[str] = None

class ConversationRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

def run_research_job(job_id: str, query: str, n_results: int, conversation_id: Optional[str] = None):
    """Run the research job synchronously."""
    from datetime import datetime
    
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = "Starting research..."
        jobs[job_id]["created_at"] = datetime.now().isoformat()
        
        result = graph.invoke({
            "query": query,
            "fetched_docs": [],
            "vector_results": [],
            "graph_results": [],
            "final_context": "",
            "next_step": ""
        }, {"recursion_limit": 50})
        
        # Extract sources and create citations
        sources = []
        citations = []
        if "fetched_docs" in result:
            for idx, doc in enumerate(result.get("fetched_docs", []), 1):
                url = doc.get("url", "")
                sources.append({"url": url, "title": url})
                citations.append({
                    "id": idx,
                    "url": url,
                    "title": url.split("/")[-1] or url
                })
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result.get("final_context", "")
        jobs[job_id]["sources"] = sources
        jobs[job_id]["citations"] = citations
        jobs[job_id]["progress"] = "Research completed!"
        
        # Store in conversation history if conversation_id provided
        if conversation_id:
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            conversations[conversation_id].append({
                "query": query,
                "result": result.get("final_context", ""),
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error in research job {job_id}: {e}", exc_info=True)
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"] = f"Error: {str(e)}"

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/research", response_model=ResearchResponse)
async def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Create a new research job."""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "queued",
        "query": request.query,
        "progress": "Job queued",
        "result": None,
        "sources": None,
        "citations": None,
        "error": None
    }
    
    n_results = request.n_results or Config.N_RESULTS
    
    # Run job in background
    background_tasks.add_task(run_research_job, job_id, request.query, n_results, None)
    
    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message="Research job created successfully"
    )

@app.post("/api/conversation", response_model=ResearchResponse)
async def create_conversation_research(request: ConversationRequest, background_tasks: BackgroundTasks):
    """Create a research job within a conversation context."""
    from datetime import datetime
    
    job_id = str(uuid.uuid4())
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    jobs[job_id] = {
        "status": "queued",
        "query": request.query,
        "conversation_id": conversation_id,
        "progress": "Job queued",
        "result": None,
        "sources": None,
        "citations": None,
        "error": None
    }
    
    n_results = Config.N_RESULTS
    
    # Run job in background
    background_tasks.add_task(run_research_job, job_id, request.query, n_results, conversation_id)
    
    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message="Research job created successfully"
    )

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a research job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress"),
        result=job.get("result"),
        sources=job.get("sources"),
        error=job.get("error")
    )

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "query": job.get("query", ""),
                "created_at": job.get("created_at")
            }
            for job_id, job in jobs.items()
        ]
    }

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del jobs[job_id]
    return {"message": "Job deleted successfully"}

@app.get("/api/export/{job_id}")
async def export_job(job_id: str):
    """Export job results in various formats."""
    from fastapi.responses import Response
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Format: Markdown with citations
    markdown = f"# Research Results\n\n"
    markdown += f"**Query:** {job['query']}\n\n"
    markdown += f"## Results\n\n{job['result']}\n\n"
    
    if job.get("citations"):
        markdown += "## Sources\n\n"
        for citation in job["citations"]:
            markdown += f"{citation['id']}. [{citation['title']}]({citation['url']})\n"
    
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=research-{job_id}.md"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
