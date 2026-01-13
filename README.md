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

Implements Retrieval-Augmented Generation pipeline:

**Text Splitter**: Uses LangChain's `RecursiveCharacterTextSplitter` to chunk documents
- Default chunk size: 1000 characters
- Default overlap: 200 characters

**Embeddings**: Generates embeddings using Google AI Studio's `models/text-embedding-004` model

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
USER_AGENT=Your Name <your_email@example.com>

# Optional (defaults provided)
DATA_DIR=./data/10k_filings
CHROMA_DB_DIR=./data/chroma_db
EMBEDDING_MODEL=models/text-embedding-004
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
   - Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. **"No filings found for ticker"**
   - Check ticker symbol is valid (use standard symbols: AAPL, MSFT, GOOGL, AMZN)
   - Some companies may not have recent 10-K filings available
   - Ensure internet connectivity for SEC EDGAR access
   - Try fetching again if initial attempt failed

3. **"Error generating embeddings"**
   - Verify Google AI Studio API key is valid and active
   - Check API rate limits - the free tier has usage restrictions
   - Ensure sufficient API credits/quota available
   - Wait 15-30 seconds between large indexing operations

4. **"Empty or no response from query"**
   - **Ensure documents are indexed**: Check that "Fetch & Index Filings" completed successfully
   - **Use specific queries**: Include company name/ticker and specific metric (e.g., "AAPL revenue 2022")
   - **Check indexed companies**: Only query companies whose filings you've indexed
   - **Verify document count**: Check if the vector database shows indexed documents
   - **Try rephrasing**: Use more specific terms (e.g., "fiscal year 2022" instead of "2022")

5. **"Query returns wrong information"**
   - Be more specific with time periods (use "fiscal year 2022" not just "2022")
   - Include both company ticker and full name for clarity
   - Check if you're comparing the right companies
   - Ensure the indexed filings cover the time period you're asking about

6. **ChromaDB errors**
   - Delete `data/chroma_db` directory and reinitialize
   - Check write permissions in the data directory
   - Ensure sufficient disk space

7. **"Rate limit exceeded" or "429 errors"**
   - **This is common with Google AI Free tier** which has strict rate limits:
     - Gemini 1.5 Flash: 15 requests per minute
     - Each query makes 3-5 API calls due to the agent architecture
   - **Automatic retry with exponential backoff**: The system now automatically waits 60s, 120s, then 240s between retries
   - **What to do**:
     - Wait 2-3 minutes before trying again (the system handles this automatically)
     - Simplify your query to use fewer tool calls
     - Avoid making multiple rapid queries in succession
     - Consider upgrading to a paid API tier for production use with heavy traffic
   - **See `RATE_LIMITING_FIX.md`** for detailed information about rate limiting strategy

### Performance Tips

- **Index fewer filings initially**: Start with 1 filing per company to test
- **Use specific queries**: More specific = better results
- **Wait between operations**: Give the API time to process
- **Clear old data**: Remove old vector store data before re-indexing
- **Monitor token usage**: Large documents consume more tokens

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
