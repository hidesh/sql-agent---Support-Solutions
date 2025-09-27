import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "example.db"

# OpenAI API key fra environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
