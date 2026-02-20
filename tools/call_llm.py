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
    client = genai.Client(api_key="AIzaSyCTyEdp66wslCOQAnG9SLofxXuUGUelQBc")
    model = "gemini-2.5-pro"
    return client.models.generate_content(model=model, contents=prompt).text