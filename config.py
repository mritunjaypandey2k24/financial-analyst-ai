"""Configuration settings for the Financial Analyst AI system."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data" / "10k_filings"))
CHROMA_DB_DIR = Path(os.getenv("CHROMA_DB_DIR", BASE_DIR / "data" / "chroma_db"))

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Google AI Studio Configuration
GOOGLE_AI_STUDIO_API_KEY = os.getenv("GOOGLE_AI_STUDIO_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")

# SEC EDGAR Configuration
USER_AGENT = os.getenv("USER_AGENT", "Financial Analyst AI research@example.com")

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 2  # Reduced from 3 to minimize token usage

# Predefined tickers for analysis
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]
