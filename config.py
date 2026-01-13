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
MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", BASE_DIR / "data" / "model_cache"))

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Hugging Face Model Configuration
# Embedding model for document embeddings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", 
    "sentence-transformers/all-MiniLM-L6-v2"  # Fast, efficient model for embeddings
)

# LLM model for text generation and analysis
LLM_MODEL = os.getenv(
    "LLM_MODEL", 
    "meta-llama/Llama-3.2-3B-Instruct"  # Lightweight instruction-tuned model
)

# Alternative models that can be used:
# For embeddings:
#   - "sentence-transformers/all-mpnet-base-v2" (higher quality, slower)
#   - "BAAI/bge-small-en-v1.5" (good balance)
#   - "sentence-transformers/all-MiniLM-L6-v2" (fast, smaller)
# For LLM:
#   - "microsoft/Phi-3-mini-4k-instruct" (3.8B params, good for chat)
#   - "meta-llama/Llama-3.2-1B-Instruct" (1B params, very fast)
#   - "HuggingFaceH4/zephyr-7b-beta" (7B params, high quality)

# Model loading configuration
USE_8BIT_QUANTIZATION = os.getenv("USE_8BIT_QUANTIZATION", "true").lower() == "true"
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# SEC EDGAR Configuration
USER_AGENT = os.getenv("USER_AGENT", "Financial Analyst AI research@example.com")

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 2  # Reduced from 3 to minimize token usage

# Local model inference configuration
BATCH_SIZE = 8  # Batch size for embedding generation
DEVICE = "auto"  # auto, cuda, cpu

# Predefined tickers for analysis
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]
