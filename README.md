# Financial Analyst AI

An AI-powered system for analyzing SEC 10-K filings using Retrieval-Augmented Generation (RAG) and Large Language Models.

## 🎯 Overview

Financial Analyst AI enables users to query and analyze SEC 10-K filings through natural language, leveraging the power of Google AI Studio's Gemini models combined with a vector database for efficient document retrieval. The system can fetch filings, process them, and answer comparative financial analysis questions.

## ✨ Features

- **Automated Data Ingestion**: Fetch SEC 10-K filings directly from the EDGAR database
- **Intelligent Document Processing**: Split and chunk documents for optimal retrieval
- **Vector Search**: Fast similarity search using ChromaDB and Google AI embeddings
- **AI-Powered Analysis**: Natural language queries answered by Gemini models
- **Comparative Analysis**: Compare financial metrics across multiple companies
- **Interactive UI**: User-friendly Streamlit interface with visualizations

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
- Google AI Studio API key

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

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google AI Studio API key
   ```

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run frontend/app.py
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Enter your Google AI Studio API key if not in .env
   - Select companies to analyze
   - Click "Fetch & Index Filings"
   - Start asking questions!

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

- "What was Apple's revenue in 2022?"
- "Compare AAPL and MSFT revenues in fiscal year 2022"
- "What are the main risk factors for Microsoft?"
- "How did Google's operating income change year-over-year?"
- "Compare profit margins between Apple and Amazon"

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

Implements Retrieval-Augmented Generation pipeline:

**Text Splitter**: Uses LangChain's `RecursiveCharacterTextSplitter` to chunk documents
- Default chunk size: 1000 characters
- Default overlap: 200 characters

**Embeddings**: Generates embeddings using Google AI Studio's `models/embedding-001` model

**Vector Store**: ChromaDB for efficient similarity search
- Persistent storage
- Metadata filtering support
- Fast retrieval

### 3. AI Agent Module

LangChain-based agent with specialized tools:

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
# Required
GOOGLE_AI_STUDIO_API_KEY=your_google_ai_studio_api_key_here

# Optional (defaults provided)
DATA_DIR=./data/10k_filings
CHROMA_DB_DIR=./data/chroma_db
EMBEDDING_MODEL=models/embedding-001
LLM_MODEL=gemini-1.5-flash
```

## 🔒 Security & Privacy

- API keys are stored locally and only used for Google AI Studio API calls
- SEC filings are public data
- No user data is transmitted to third parties except Google AI Studio
- All data processing can be done locally

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

1. **"Google AI Studio API key not set"**
   - Ensure `.env` file exists with valid `GOOGLE_AI_STUDIO_API_KEY`
   - Or set it in the Streamlit sidebar

2. **"No filings found for ticker"**
   - Check ticker symbol is valid
   - Some companies may not have recent 10-K filings
   - Ensure internet connectivity

3. **"Error generating embeddings"**
   - Verify Google AI Studio API key is valid
   - Check API rate limits
   - Ensure sufficient API credits

4. **ChromaDB errors**
   - Delete `data/chroma_db` directory and reinitialize
   - Check write permissions

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

- **LangChain**: Framework for LLM applications
- **Google AI Studio**: Gemini models and embeddings
- **ChromaDB**: Vector database
- **Streamlit**: Web framework
- **SEC EDGAR**: Financial data source

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Disclaimer**: This tool is for research and educational purposes only. Always verify financial information from official sources. Past performance does not guarantee future results.
