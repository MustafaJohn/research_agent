from tools.fetch_web import FetchWebTool
from orchestration.state import ResearchState
from config import Config

def research_agent(state: ResearchState) -> ResearchState:
    n_results = Config.N_RESULTS
    docs = FetchWebTool().fetch_query("Academic Research areas on " + state["query"], n_results=n_results)
    valid_docs = []

    for doc in docs:
        if is_valid_text(doc["text"]):
            valid_docs.append(doc)
        else:
            print("[research] Skipped non-text or binary document")

    state["fetched_docs"] = valid_docs
    return state

def is_valid_text(text: str) -> bool:
    if len(text) < 200:
        return False
    if "\x00" in text:
        return False
    if text.count("obj") > 10 and "stream" in text:
        return False
    return True
