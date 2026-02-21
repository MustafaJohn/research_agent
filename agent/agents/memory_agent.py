from memory.chunker import chunk_text
#from memory.graph_memory import GraphMemory
from memory.vector_memory import VectorMemory
from orchestration.state import ResearchState
import time

#graph_mem = GraphMemory()

def memory_agent(state: ResearchState, vector_mem: VectorMemory) -> ResearchState:
    """
    Docstring for memory_agent
    
    :param state: Description
    :type state: ResearchState
    :return: Description
    :rtype: Any
    """
    print("[memory] Storing fetched documents into memory...")
    all_chunks = []

    # Chunk ONCE
    for doc in state["fetched_docs"]:
        chunks = chunk_text(doc["text"])
        for chunk_id, chunk_text_ in chunks:
            all_chunks.append((doc["url"], chunk_id, chunk_text_))
    
    #print("Chunking process over", time.strftime("%X"))
    print("[memory] Storing into vector and graph memory...")
    
    # Vector memory
    for url, chunk_id, text in all_chunks:
        vector_mem.add_chunks(url, [(chunk_id, text)])
    #print("Storing process over in vector memory", time.strftime("%X"))
    
    # Graph memory
    #for url, chunk_id, text in all_chunks:
    #    graph_mem.add_chunk(url, chunk_id, text)
    #print("Storing process over in graph memory", time.strftime("%X"))
    
    return state

