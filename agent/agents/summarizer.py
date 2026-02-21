# agents/summarizer.py
from time import sleep

from tools.call_llm import call_llm
from orchestration.state import ResearchState

def summarizer_agent(state: ResearchState) -> ResearchState:
    from config import Config
    import logging
    
    logger = logging.getLogger(__name__)
    
    prompt = f"""
    Give some potential research areas using the context below. 

    Query:
    {state['query']}

    Context:
    {state['final_context']}
    """
    trials = Config.MAX_RETRIES
    for no in range(trials):
        try:
            print("Calling LLM for summarization...")
            print(f"Attempt {no + 1} of {trials}")
            result = call_llm(prompt)
            state["final_context"] = result
            return state
        except Exception as e:
            logger.error(f"Error calling LLM: {e}. Retrying...")
            sleep(3)  # Wait before retrying
            continue
    logger.error("Failed to call LLM after multiple attempts.")
    state["final_context"] = "Error: Failed to generate summary after multiple attempts."
    return state