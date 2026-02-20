"""
CLI entry point for the Research Agent.
"""
from orchestration.graph import build_graph
from config import Config
from utils.logging_config import setup_logging

def main():
    """Main CLI function."""
    setup_logging()
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        Config.validate()
        Config.ensure_directories()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY in your environment variables or .env file")
        return
    
    graph = build_graph()
    
    print("=== Multi-Agent Research System ===")
    print("Type 'quit' or 'exit' to stop\n")

    while True:
        try:
            q = input("\nEnter your Research Area> ").strip()
            if q.lower() in {"quit", "exit"}:
                break
            
            if not q:
                print("Please enter a valid research topic.")
                continue

            print("\nProcessing... This may take a few moments.")
            result = graph.invoke({
                "query": q,
                "fetched_docs": [],
                "vector_results": [],
                "graph_results": [],
                "final_context": "",
                "next_step": ""
            }, {"recursion_limit": 50})

            print("\n" + "="*60)
            print("FINAL ANSWER:")
            print("="*60 + "\n")
            print(result["final_context"])
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\nError: {e}")
            print("Please try again or check the logs for more details.")

if __name__ == "__main__":
    main()


