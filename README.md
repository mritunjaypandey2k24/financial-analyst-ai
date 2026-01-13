# Financial Analyst AI

An AI-powered system for analyzing SEC 10-K filings using Retrieval-Augmented Generation (RAG) and local Hugging Face models.

## 🎯 Overview

Financial Analyst AI enables users to query and analyze SEC 10-K filings through natural language, leveraging open-source Hugging Face models combined with a vector database for efficient document retrieval. The system runs entirely locally, providing privacy, cost-effectiveness, and unlimited usage without API rate limits.

## ✨ Features

- **Automated Data Ingestion**: Fetch SEC 10-K filings directly from the EDGAR database
- **Intelligent Document Processing**: Split and chunk documents for optimal retrieval
- **Vector Search**: Fast similarity search using ChromaDB and local Hugging Face embeddings
- **AI-Powered Analysis**: Natural language queries answered by local LLM models
- **Comparative Analysis**: Compare financial metrics across multiple companies
- **Interactive UI**: User-friendly Streamlit interface with visualizations
- **Fully Local**: No external API dependencies, complete privacy and control
- **No Rate Limits**: Process unlimited queries without API restrictions
- **Cost-Free**: No API fees after initial setup

## 🏗️ Architecture

```
financial-analyst-ai/
├── data_ingestion/          # SEC filing fetching and parsing
│   ├── __init__.py
│   └── fetch_10k.py        # Main fetching logic
├── rag_engine/             # RAG pipeline components
│   ├── __init__.py
│   ├── text_splitter.py   # Document chunking
│   ├── embeddings.py      # Embedding generation
│   └── vector_store.py    # ChromaDB integration
├── agent/                  # AI agent implementation
│   ├── __init__.py
│   └── financial_agent.py # LangChain agent with tools
├── frontend/               # Streamlit UI
│   ├── __init__.py
│   └── app.py             # Main application
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_data_ingestion.py
│   ├── test_rag_engine.py
│   └── test_integration.py
├── docs/                   # Documentation
├── data/                   # Data storage (created at runtime)
│   ├── 10k_filings/       # Downloaded filings
│   └── chroma_db/         # Vector database
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 5GB free disk space for models
- (Optional) NVIDIA GPU with 6GB+ VRAM for faster inference

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mritunjaypandey2k24/financial-analyst-ai.git
   cd financial-analyst-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (Optional)
   ```bash
   cp .env.example .env
   # Edit .env to customize model settings if desired
   # Default models work well out of the box
   ```

5. **Download models on first run**
   ```bash
   # Models will be downloaded automatically on first use
   # This requires internet connection initially
   # Models are cached locally for offline use
   ```

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run frontend/app.py
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Select companies to analyze
   - Click "Fetch & Index Filings"
   - Start asking questions!

**Note**: First run will download models (~3-4GB). This requires internet connection but only needs to be done once.

## 📖 Usage Examples

### Command Line Usage

#### Fetch SEC Filings

```python
from data_ingestion import SECFilingFetcher

fetcher = SECFilingFetcher()
filings = fetcher.fetch_10k_filing("AAPL", num_filings=1)
print(f"Fetched {len(filings)} filing(s)")
```

#### Use RAG Engine

```python
from rag_engine import RAGEngine

rag = RAGEngine()

# Add documents
documents = [
    {
        'content': 'Apple Inc. reported revenue of $394.3 billion...',
        'ticker': 'AAPL',
        'filing_date': '2022-10-28',
        'file_path': '/path/to/filing.txt'
    }
]
rag.add_documents(documents)

# Search
results = rag.search("What was the revenue?", k=5)
```

#### Use AI Agent

```python
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent

rag = RAGEngine()
# ... add documents ...

agent = FinancialAnalystAgent(rag)
response = agent.query("Compare Apple and Microsoft revenues in 2022")
print(response)
```

### Example Queries

The system works best with specific, well-formatted queries. Here are examples:

#### Single Company Queries
- "What was Apple's revenue in fiscal year 2022?"
- "What was the total revenue of AAPL in fiscal year 2022 according to the 10-K filings?"
- "How much did Microsoft earn in 2022?"
- "What are Google's main sources of revenue?"
- "What were Amazon's operating expenses in fiscal year 2021?"

#### Comparative Queries
- "Compare AAPL and MSFT revenues in fiscal year 2022"
- "How do Apple and Microsoft profit margins compare?"
- "Which had higher growth: Amazon or Google?"

#### Trend Analysis
- "How did Apple's revenue change year-over-year?"
- "What is the growth trend for Microsoft's cloud business?"

#### Risk and Strategy
- "What are the main risk factors for Microsoft?"
- "What is Apple's strategy for expanding services revenue?"

**Query Best Practices:**
- ✅ Include specific company names or ticker symbols (AAPL, MSFT, GOOGL, AMZN)
- ✅ Specify time periods (fiscal year 2022, FY2022, 2021-2022)
- ✅ Mention specific metrics (revenue, net income, profit margin, expenses)
- ✅ Be explicit about what you're comparing
- ❌ Avoid vague queries like "Tell me about Apple"
- ❌ Don't ask about companies without indexed filings

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_ingestion.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Note**: Integration tests require a Google AI Studio API key to be set.

## 📊 System Components

### 1. Data Ingestion Module

Fetches SEC 10-K filings from the EDGAR database using the `sec-edgar-downloader` library.

**Key Features:**
- Downloads filings for specified tickers
- Parses HTML content to extract text
- Handles both HTML and plain text formats
- Supports batch fetching for multiple companies

### 2. RAG Engine Module

Implements Retrieval-Augmented Generation pipeline using local models:

**Text Splitter**: Uses LangChain's `RecursiveCharacterTextSplitter` to chunk documents
- Default chunk size: 1000 characters
- Default overlap: 200 characters

**Embeddings**: Generates embeddings using Hugging Face `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Fast local inference
- No API calls or rate limits

**Vector Store**: ChromaDB for efficient similarity search
- Persistent storage
- Metadata filtering support
- Fast retrieval

### 3. AI Agent Module

LangChain-based agent using local Hugging Face models with specialized tools:

**Local LLM**: Uses `meta-llama/Llama-3.2-3B-Instruct` (or configured model)
- Runs entirely on your machine
- Optional 8-bit quantization for memory efficiency
- GPU acceleration when available

**Tools:**
- `search_financial_filings`: Search across all indexed filings
- `search_ticker_specific`: Search within a specific company's filings
- `compare_companies`: Compare data between two companies

**Agent Capabilities:**
- Natural language understanding
- Multi-step reasoning
- Context-aware responses
- Citation of sources

### 4. Frontend (Streamlit)

Interactive web interface with:
- API key configuration
- Ticker selection
- Filing fetching and indexing
- Query input
- Result display
- Example queries
- System information

## ⚙️ Configuration

Edit `.env` file or set environment variables:

```bash
# Model Selection
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct

# Performance Settings
USE_8BIT_QUANTIZATION=true  # Reduces memory by ~50%
USE_GPU=true                # Enable GPU acceleration
MAX_NEW_TOKENS=512          # Maximum response length
TEMPERATURE=0.1             # Lower = more focused

# Storage
DATA_DIR=./data/10k_filings
CHROMA_DB_DIR=./data/chroma_db
MODEL_CACHE_DIR=./data/model_cache

# SEC EDGAR
USER_AGENT=Your Name <your_email@example.com>
```

### Model Options

**Embedding Models:**
- `sentence-transformers/all-MiniLM-L6-v2` - Default, fast and lightweight (80MB)
- `sentence-transformers/all-mpnet-base-v2` - Higher quality (420MB)
- `BAAI/bge-small-en-v1.5` - Good balance (130MB)

**LLM Models:**
- `meta-llama/Llama-3.2-3B-Instruct` - Default, balanced (3GB)
- `meta-llama/Llama-3.2-1B-Instruct` - Faster, smaller (1GB)
- `microsoft/Phi-3-mini-4k-instruct` - Compact chat model (4GB)
- `HuggingFaceH4/zephyr-7b-beta` - Higher quality (7GB)

See `HUGGINGFACE_MIGRATION_GUIDE.md` for detailed model selection guidance.

## 🔒 Security & Privacy

- All processing happens locally on your machine
- No data is sent to external services (except SEC EDGAR for public filings)
- Models run entirely offline after initial download
- SEC filings are public data
- Full control over your data and computations

## 📝 Development

### Adding New Features

1. **New Data Source**: Extend `data_ingestion/fetch_10k.py`
2. **Custom Chunking**: Modify `rag_engine/text_splitter.py`
3. **Additional Tools**: Add tools in `agent/financial_agent.py`
4. **UI Enhancements**: Update `frontend/app.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public functions
- Write tests for new features

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError" errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're using Python 3.8+
   - Try `pip install --upgrade -r requirements.txt`

2. **"No filings found for ticker"**
   - Check ticker symbol is valid (use standard symbols: AAPL, MSFT, GOOGL, AMZN)
   - Some companies may not have recent 10-K filings available
   - Ensure internet connectivity for SEC EDGAR access
   - Try fetching again if initial attempt failed

3. **"Out of memory" errors**
   - Enable 8-bit quantization: `USE_8BIT_QUANTIZATION=true`
   - Use smaller models (see configuration section)
   - Close other applications to free RAM
   - Reduce `BATCH_SIZE` in config.py

4. **Slow inference speed**
   - Enable GPU if available: `USE_GPU=true` and install CUDA PyTorch
   - Use smaller/faster models like `Llama-3.2-1B-Instruct`
   - Reduce `MAX_NEW_TOKENS` to limit response length
   - Consider upgrading hardware

5. **"Error downloading model" or connection errors**
   - Check internet connection (only needed for first run)
   - Models are downloaded from Hugging Face Hub
   - Downloads resume automatically if interrupted
   - Check firewall/proxy settings
   - Manually download models if needed

6. **"Empty or no response from query"**
   - **Ensure documents are indexed**: Check that "Fetch & Index Filings" completed successfully
   - **Use specific queries**: Include company name/ticker and specific metric (e.g., "AAPL revenue 2022")
   - **Check indexed companies**: Only query companies whose filings you've indexed
   - **Verify document count**: Check if the vector database shows indexed documents
   - **Try rephrasing**: Use more specific terms (e.g., "fiscal year 2022" instead of "2022")

7. **ChromaDB errors**
   - Delete `data/chroma_db` directory and reinitialize
   - Check write permissions in the data directory
   - Ensure sufficient disk space

### Performance Tips

- **First run**: Models download automatically (~3-4GB), requires internet
- **Use GPU**: Install CUDA PyTorch for 5-10x speedup
- **Enable quantization**: Set `USE_8BIT_QUANTIZATION=true` to reduce memory
- **Choose appropriate models**: Balance between quality and speed for your hardware
- **Index fewer filings initially**: Start with 1 filing per company to test
- **Use specific queries**: More specific = better results
- **Clear old data**: Remove old vector store data before re-indexing

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- **Hugging Face**: Transformers library and model hub
- **LangChain**: Framework for LLM applications
- **Sentence Transformers**: Embedding models
- **ChromaDB**: Vector database
- **Streamlit**: Web framework
- **SEC EDGAR**: Financial data source
- **Meta AI**: Llama models
- **Microsoft**: Phi models

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Disclaimer**: This tool is for research and educational purposes only. Always verify financial information from official sources. Past performance does not guarantee future results.
