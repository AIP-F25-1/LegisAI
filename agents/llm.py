import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

def llama_llm():
    return LLM(
        model=os.getenv("OPENAI_MODEL", "llama3.1:8b-instruct"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2048")),
    )
