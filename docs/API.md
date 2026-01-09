# API Documentation

## Data Ingestion Module

### SECFilingFetcher

Fetches and processes SEC 10-K filings from the EDGAR database.

#### Constructor

```python
SECFilingFetcher(data_dir: Optional[Path] = None)
```

**Parameters:**
- `data_dir`: Directory to store downloaded filings. Defaults to `config.DATA_DIR`

#### Methods

##### fetch_10k_filing

```python
fetch_10k_filing(ticker: str, num_filings: int = 1) -> List[Dict[str, str]]
```

Fetch 10-K filings for a given ticker.

**Parameters:**
- `ticker`: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
- `num_filings`: Number of recent filings to fetch (default: 1)

**Returns:**
- List of dictionaries containing filing information with keys:
  - `ticker`: Stock ticker
  - `filing_date`: Date of the filing
  - `file_path`: Path to the filing file
  - `content`: Extracted text content
  - `raw_content`: Raw HTML/text content

##### fetch_multiple_tickers

```python
fetch_multiple_tickers(tickers: List[str], num_filings: int = 1) -> Dict[str, List[Dict[str, str]]]
```

Fetch 10-K filings for multiple tickers.

**Parameters:**
- `tickers`: List of stock ticker symbols
- `num_filings`: Number of recent filings to fetch per ticker (default: 1)

**Returns:**
- Dictionary mapping tickers to their filing information

##### get_filing_text

```python
get_filing_text(ticker: str, filing_index: int = 0) -> Optional[str]
```

Get the text content of a specific filing.

**Parameters:**
- `ticker`: Stock ticker symbol
- `filing_index`: Index of the filing (0 = most recent)

**Returns:**
- Text content of the filing or None if not found

---

## RAG Engine Module

### DocumentChunker

Handles text splitting for RAG pipeline.

#### Constructor

```python
DocumentChunker(chunk_size: int = None, chunk_overlap: int = None)
```

**Parameters:**
- `chunk_size`: Size of each text chunk (default: from config.CHUNK_SIZE)
- `chunk_overlap`: Overlap between chunks (default: from config.CHUNK_OVERLAP)

#### Methods

##### split_text

```python
split_text(text: str) -> List[str]
```

Split text into chunks.

**Parameters:**
- `text`: Input text to split

**Returns:**
- List of text chunks

##### split_documents

```python
split_documents(documents: List[dict]) -> List[dict]
```

Split multiple documents into chunks with metadata.

**Parameters:**
- `documents`: List of document dictionaries with 'content' and metadata

**Returns:**
- List of chunk dictionaries with metadata including:
  - `content`: Chunk text
  - `chunk_id`: Index of the chunk
  - `ticker`: Stock ticker
  - `filing_date`: Filing date
  - `source_file`: Source file path

### EmbeddingGenerator

Generates embeddings for text chunks using Google AI Studio.

#### Constructor

```python
EmbeddingGenerator(model: str = None)
```

**Parameters:**
- `model`: Google AI embedding model name (default: from config.EMBEDDING_MODEL)

#### Methods

##### generate_embedding

```python
generate_embedding(text: str) -> List[float]
```

Generate embedding for a single text.

**Parameters:**
- `text`: Input text

**Returns:**
- Embedding vector (list of floats)

##### generate_embeddings

```python
generate_embeddings(texts: List[str]) -> List[List[float]]
```

Generate embeddings for multiple texts.

**Parameters:**
- `texts`: List of input texts

**Returns:**
- List of embedding vectors

### RAGEngine

Main RAG engine for document storage and retrieval.

#### Constructor

```python
RAGEngine(collection_name: str = "financial_filings")
```

**Parameters:**
- `collection_name`: Name of the ChromaDB collection (default: "financial_filings")

#### Methods

##### add_documents

```python
add_documents(documents: List[Dict[str, str]]) -> None
```

Add documents to the vector store.

**Parameters:**
- `documents`: List of document dictionaries with 'content' and metadata

##### search

```python
search(query: str, k: int = None, filter_dict: Optional[Dict] = None) -> List[Dict]
```

Search for relevant documents using similarity search.

**Parameters:**
- `query`: Search query
- `k`: Number of results to return (default: from config.TOP_K_RESULTS)
- `filter_dict`: Optional metadata filter (e.g., `{'ticker': 'AAPL'}`)

**Returns:**
- List of relevant document chunks with:
  - `content`: Document text
  - `metadata`: Document metadata
  - `score`: Similarity score

##### search_by_ticker

```python
search_by_ticker(query: str, ticker: str, k: int = None) -> List[Dict]
```

Search for documents related to a specific ticker.

**Parameters:**
- `query`: Search query
- `ticker`: Stock ticker symbol
- `k`: Number of results to return

**Returns:**
- List of relevant document chunks

##### get_context_for_query

```python
get_context_for_query(query: str, k: int = None) -> str
```

Get formatted context for a query.

**Parameters:**
- `query`: Search query
- `k`: Number of results to return

**Returns:**
- Formatted context string with sources

##### clear_collection

```python
clear_collection() -> None
```

Clear all documents from the collection.

---

## AI Agent Module

### FinancialAnalystAgent

AI Agent for financial analysis and comparative queries.

#### Constructor

```python
FinancialAnalystAgent(rag_engine)
```

**Parameters:**
- `rag_engine`: Instance of RAGEngine for document retrieval

#### Methods

##### query

```python
query(question: str) -> str
```

Process a financial analysis query.

**Parameters:**
- `question`: User's question about financial data

**Returns:**
- Agent's response as a string

##### analyze_comparative

```python
analyze_comparative(ticker1: str, ticker2: str, metric: str) -> str
```

Perform comparative analysis between two companies.

**Parameters:**
- `ticker1`: First company ticker
- `ticker2`: Second company ticker
- `metric`: Financial metric to compare (e.g., 'revenue', 'profit')

**Returns:**
- Comparative analysis as a string

---

## Configuration

Configuration is managed through the `config.py` module and environment variables.

### Environment Variables

- `GOOGLE_AI_STUDIO_API_KEY`: Google AI Studio API key (required)
- `DATA_DIR`: Directory for storing SEC filings (default: `./data/10k_filings`)
- `CHROMA_DB_DIR`: Directory for ChromaDB database (default: `./data/chroma_db`)
- `EMBEDDING_MODEL`: Google AI embedding model (default: `models/embedding-001`)
- `LLM_MODEL`: Google AI LLM model (default: `gemini-1.5-flash`)
- `USER_AGENT`: User agent for SEC EDGAR requests

### Configuration Constants

- `CHUNK_SIZE`: 1000 - Size of text chunks for splitting
- `CHUNK_OVERLAP`: 200 - Overlap between chunks
- `TOP_K_RESULTS`: 5 - Number of results to return in searches
- `DEFAULT_TICKERS`: ["AAPL", "MSFT", "GOOGL", "AMZN"] - Default tickers for analysis

---

## Error Handling

All modules implement comprehensive error handling:

- **Data Ingestion**: Returns empty lists/None on errors, logs warnings
- **RAG Engine**: Raises exceptions on initialization failures, returns empty results on search errors
- **Agent**: Returns error messages in response strings
- **Frontend**: Displays user-friendly error messages

### Common Exceptions

- `Exception`: Generic errors with descriptive messages
- API rate limit errors from Google AI Studio
- Network errors when fetching SEC filings
- ChromaDB initialization errors

---

## Examples

### Complete Pipeline Example

```python
import config
from data_ingestion import SECFilingFetcher
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent

# Set API key
config.GOOGLE_AI_STUDIO_API_KEY = "your-api-key"

# Fetch filings
fetcher = SECFilingFetcher()
filings = fetcher.fetch_multiple_tickers(["AAPL", "MSFT"], num_filings=1)

# Initialize RAG engine
rag = RAGEngine()

# Add documents
all_docs = []
for ticker, ticker_filings in filings.items():
    all_docs.extend(ticker_filings)
rag.add_documents(all_docs)

# Create agent
agent = FinancialAnalystAgent(rag)

# Query
response = agent.query("Compare the revenues of Apple and Microsoft")
print(response)
```

### Search with Filters

```python
from rag_engine import RAGEngine

rag = RAGEngine()

# Search only in Apple's filings
results = rag.search(
    "What was the revenue?",
    k=5,
    filter_dict={'ticker': 'AAPL'}
)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Content: {result['content'][:100]}...")
```

### Custom Chunking

```python
from rag_engine.text_splitter import DocumentChunker

# Create custom chunker
chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)

# Split text
chunks = chunker.split_text("Your long document text here...")
print(f"Created {len(chunks)} chunks")
```
