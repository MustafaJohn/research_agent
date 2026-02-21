from orchestration.state import ResearchState

def context_builder_agent(state: ResearchState) -> ResearchState:
    parts = []

    vector_results = state.get("vector_results", [])
    graph_results = state.get("graph_results", [])

    if not vector_results and not graph_results:
        state["final_context"] = ""
        return state

    # Vector memory context
    for item in vector_results:
        parts.append(
            f"[SOURCE]\n{item.get('chunk', '')}"
        )

    # Graph memory context
    for rel in graph_results:
        parts.append(
            f"[GRAPH]\n{rel['source']} --{rel['relation']}--> {rel['target']}"
        )

    state["final_context"] = "\n\n".join(parts)
    return state
