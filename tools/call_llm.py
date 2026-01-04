# call_llm.py
import google.genai as genai

def call_llm(prompt: str) -> str:
    client = genai.Client(api_key=API_KEY)
    model = "gemini-3-pro-preview"
    return client.models.generate_content(model=model, contents=prompt).text
