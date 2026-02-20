"""
Startup script for the Research Agent API server.
"""
import os
import sys
from pathlib import Path
import uvicorn
from config import Config

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    
    
    # Validate configuration
    try:
        Config.validate()
        Config.ensure_directories()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set GEMINI_API_KEY in your environment variables or .env file")
        sys.exit(1)
    
    # Start server
    uvicorn.run(
        "api.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )
