# Getting Started with Financial Analyst AI

## Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mritunjaypandey2k24/financial-analyst-ai.git
cd financial-analyst-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your Google AI Studio API key:

```
GOOGLE_AI_STUDIO_API_KEY=your_api_key_here
```

### 3. Running the Application

#### Option A: Web Interface (Recommended)

```bash
streamlit run frontend/app.py
```

Then open your browser to `http://localhost:8501`

#### Option B: Programmatic Usage

```python
from data_ingestion import SECFilingFetcher
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent

# Fetch filings
fetcher = SECFilingFetcher()
filings = fetcher.fetch_10k_filing("AAPL", num_filings=1)

# Initialize RAG engine
rag = RAGEngine()
rag.add_documents(filings)

# Create agent and query
agent = FinancialAnalystAgent(rag)
response = agent.query("What was Apple's revenue in 2022?")
print(response)
```

## Example Workflows

### Analyzing a Single Company

```python
from data_ingestion import SECFilingFetcher
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent

# 1. Fetch Apple's latest 10-K
fetcher = SECFilingFetcher()
aapl_filings = fetcher.fetch_10k_filing("AAPL", num_filings=1)

# 2. Process and index
rag = RAGEngine()
rag.add_documents(aapl_filings)

# 3. Query the data
agent = FinancialAnalystAgent(rag)
questions = [
    "What was the total revenue?",
    "What are the main risk factors?",
    "How did iPhone sales perform?"
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {agent.query(q)}")
```

### Comparing Multiple Companies

```python
from data_ingestion import SECFilingFetcher
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent

# 1. Fetch filings for multiple companies
fetcher = SECFilingFetcher()
tickers = ["AAPL", "MSFT", "GOOGL"]
all_filings = []

for ticker in tickers:
    filings = fetcher.fetch_10k_filing(ticker, num_filings=1)
    all_filings.extend(filings)

# 2. Process all filings
rag = RAGEngine()
rag.add_documents(all_filings)

# 3. Comparative analysis
agent = FinancialAnalystAgent(rag)
response = agent.query("Compare the revenues of Apple, Microsoft, and Google")
print(response)
```

### Using the Web Interface

1. **Launch the app**:
   ```bash
   streamlit run frontend/app.py
   ```

2. **Configure settings** in the sidebar:
   - Enter your Google AI Studio API key (if not in .env)
   - Select companies to analyze
   - Choose number of filings

3. **Fetch data**:
   - Click "Fetch & Index Filings"
   - Wait for processing to complete

4. **Ask questions**:
   - Type your query in the text area
   - Click "Analyze" to get AI-powered insights
   - Try example queries for inspiration

## Common Use Cases

### 1. Revenue Analysis

**Query**: "What was [Company]'s total revenue in [Year]?"

**Example**:
```python
agent.query("What was Apple's total revenue in 2022?")
```

### 2. Year-over-Year Comparison

**Query**: "How did [Company]'s [metric] change year-over-year?"

**Example**:
```python
agent.query("How did Microsoft's cloud revenue change year-over-year?")
```

### 3. Risk Assessment

**Query**: "What are the main risk factors for [Company]?"

**Example**:
```python
agent.query("What are the main risk factors for Google?")
```

### 4. Competitive Analysis

**Query**: "Compare [metric] between [Company A] and [Company B]"

**Example**:
```python
agent.query("Compare profit margins between Apple and Microsoft")
```

### 5. Product Performance

**Query**: "How did [Product/Segment] perform for [Company]?"

**Example**:
```python
agent.query("How did iPhone sales perform for Apple in 2022?")
```

## Tips for Best Results

### Query Formulation

1. **Be Specific**: Include company name and time period
   - ✓ "What was Apple's revenue in Q4 2022?"
   - ✗ "What was the revenue?"

2. **Use Company Names or Tickers**: Both work
   - ✓ "Compare AAPL and MSFT"
   - ✓ "Compare Apple and Microsoft"

3. **Ask One Thing at a Time**: Focus queries for better results
   - ✓ "What was the operating income?"
   - ✗ "What was the revenue, operating income, and profit margin?"

### Performance Optimization

1. **Start Small**: Fetch 1 filing per company initially
2. **Selective Indexing**: Only index companies you need
3. **Clear Cache**: Use `rag.clear_collection()` to start fresh
4. **API Costs**: Be mindful of Google AI Studio API usage

### Troubleshooting

**Problem**: "No relevant context found"
- **Solution**: Ensure filings are fetched and indexed first

**Problem**: Rate limit errors
- **Solution**: Reduce number of concurrent queries, upgrade API plan

**Problem**: "Google AI Studio API key not set"
- **Solution**: Check .env file or set in Streamlit sidebar

**Problem**: ChromaDB errors
- **Solution**: Delete `data/chroma_db` directory and reinitialize

## Advanced Features

### Custom Chunking Strategy

```python
from rag_engine.text_splitter import DocumentChunker

# Create custom chunker with specific parameters
chunker = DocumentChunker(
    chunk_size=500,
    chunk_overlap=50
)

# Use in your pipeline
chunks = chunker.split_documents(documents)
```

### Metadata Filtering

```python
# Search only in Apple's filings
results = rag.search_by_ticker(
    query="revenue information",
    ticker="AAPL",
    k=5
)
```

### Direct Search Without Agent

```python
# Use RAG engine directly for faster searches
results = rag.search("revenue trends", k=10)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Company: {result['metadata']['ticker']}")
    print(f"Content: {result['content'][:200]}...")
    print()
```

## Next Steps

1. **Explore the Code**: Review the implementation in each module
2. **Customize**: Modify parameters, add new tools, enhance UI
3. **Scale Up**: Index more filings, add more companies
4. **Deploy**: Consider cloud deployment for broader access
5. **Extend**: Add support for other SEC forms (10-Q, 8-K, etc.)

## Support

For issues, questions, or contributions:
- Check the README.md for detailed documentation
- Review docs/API.md for API reference
- Open an issue on GitHub
- Refer to inline code documentation

## License and Disclaimer

This project is for educational and research purposes only. Always verify financial information from official sources. Past performance does not guarantee future results.
