# orchestration/state.py
from typing import TypedDict, List, Dict, Any

class ResearchState(TypedDict):
    """
    Docstring for ResearchState
    """
    query: str

    fetched_docs: List[Dict[str, Any]]

    vector_results: List[Dict[str, Any]]
    graph_results: List[Dict[str, Any]]

    final_context: str
    next_step: str
    analysis_decision: str
    logs: List[str]