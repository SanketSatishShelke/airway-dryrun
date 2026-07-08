"""
Generic LLM client — currently backed by NVIDIA NIM (OpenAI-compatible endpoint),
using meta/llama-3.3-70b-instruct. Swappable to any OpenAI-compatible provider
by changing base_url/model/api_key source below.

Reads NIM_API_KEY from the project's root .env file.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file: agentic_layer/ -> project root)
PROJECT_DIR = os.environ.get("PROJECT_DIR")
if PROJECT_DIR:
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))
else:
    load_dotenv()  # fallback: look for .env in current directory

NIM_API_KEY = os.getenv("NIM_API_KEY")
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "meta/llama-3.3-70b-instruct"

if not NIM_API_KEY:
    raise ValueError("No API key found. Set NIM_API_KEY in your .env file.")

client = OpenAI(base_url=NIM_BASE_URL, api_key=NIM_API_KEY)


def generate_interpretation(prompt: str, temperature: float = 0.3, max_tokens: int = 1024) -> str:
    """
    Send a prompt to the LLM and return the generated text.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content