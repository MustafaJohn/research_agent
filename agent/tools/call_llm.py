# call_llm.py
import os
import logging
from typing import Optional
import google.genai as genai

logger = logging.getLogger(__name__)

def call_llm(prompt: str, model: Optional[str] = None) -> str:
    """
    Call the Gemini LLM API.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Optional model name override
        
    Returns:
        The generated text response
        
    Raises:
        ValueError: If API key is not set
        Exception: If API call fails
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    model_name = model or os.getenv("LLM_MODEL", "gemini-2.5-pro")
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise