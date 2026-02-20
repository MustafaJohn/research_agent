"""
Setup script to ensure proper package structure.
"""
from setuptools import setup, find_packages

setup(
    name="research-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "python-dotenv>=1.0.0",
        "langgraph>=0.0.20",
        "langchain>=0.1.0",
        "google-genai>=0.2.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "ddgs>=0.1.0",
        "PyMuPDF>=1.23.8",
        "faiss-cpu>=1.7.4",
        "sentence-transformers>=2.2.2",
        "numpy>=1.26.3",
        "networkx>=3.2.1",
        "spacy>=3.7.2",
        "python-multipart>=0.0.6",
    ],
)
