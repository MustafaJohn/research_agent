"""
Configuration management for the research agent.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import List

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

class Config:
    """Application configuration."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Search Configuration
    N_RESULTS: int = int(os.getenv("N_RESULTS", "20"))
    RATE_LIMIT: float = float(os.getenv("RATE_LIMIT", "1.5"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-pro")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    RAW_DATA_DIR: Path = BASE_DIR / os.getenv("RAW_DATA_DIR", "data/raw")
    MEMORY_INDEX_PATH: Path = BASE_DIR / os.getenv("MEMORY_INDEX_PATH", "data/memory.index")
    MEMORY_META_PATH: Path = BASE_DIR / os.getenv("MEMORY_META_PATH", "data/memory_store.json")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Analysis Thresholds
    MIN_VECTOR_HITS: int = int(os.getenv("MIN_VECTOR_HITS", "3"))
    MIN_AVG_SCORE: float = float(os.getenv("MIN_AVG_SCORE", "0.43"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is set."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.MEMORY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.MEMORY_META_PATH.parent.mkdir(parents=True, exist_ok=True)
