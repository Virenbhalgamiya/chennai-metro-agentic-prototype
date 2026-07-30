import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SOP_DIR = DATA_DIR / "mock_sops"
DB_URL = os.getenv("DB_URL", f"sqlite:///{BASE_DIR}/chennai_metro.db")

# Groq Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# RAG Config
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
FAISS_INDEX_PATH = BASE_DIR / "faiss_index"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SOP_DIR.mkdir(exist_ok=True)
FAISS_INDEX_PATH.mkdir(exist_ok=True)
