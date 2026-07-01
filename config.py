import os
from dotenv import load_dotenv

load_dotenv()  # loads keys from .env file locally

# ── Groq — free & very fast (get key at console.groq.com) ────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = "llama-3.1-8b-instant"

# ── OpenRouter — fallback if Groq fails ───────────────────────────────────────
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL    = "meta-llama/llama-3.2-3b-instruct:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_FALLBACK_MODELS = [
    "openai/gpt-oss-20b:free",
    "google/gemma-4-26b-a4b-it:free",
]

# Hugging Face — free inference API
HF_API_KEY = os.getenv("HF_API_KEY", "")
