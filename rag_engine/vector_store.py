"""
Vector Store Module

Integrates ChromaDB for efficient storage and retrieval of document embeddings.
Includes rate-limiting protection for Google AI Studio free tier.
"""
from typing import List, Dict, Optional
import time
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import config
import logging
from .text_splitter import DocumentChunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine.
    
    Handles document ingestion, embedding generation, storage in ChromaDB,
    and similarity-based retrieval.
    """
    
    def __init__(self, collection_name: str = "financial_filings"):
        """Initialize the RAG Engine."""
        self.collection_name = collection_name
        self.chunker = DocumentChunker()
        
        # Initialize embeddings
        if not config.GOOGLE_AI_STUDIO_API_KEY:
            logger.warning("GOOGLE_AI_STUDIO_API_KEY not set. RAG Engine will not work properly.")
        
        # Use config model or fallback to a stable one
        model_name = config.EMBEDDING_MODEL
        if not model_name:
            model_name = "models/text-embedding-004"

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=config.GOOGLE_AI_STUDIO_API_KEY,
            task_type="retrieval_document"
        )
        
        # Initialize ChromaDB
        self.vector_store = self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> Chroma:
        """Initialize or load the ChromaDB vector store."""
        try:
            vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(config.CHROMA_DB_DIR)
            )
            logger.info(f"Initialized vector store with collection: {self.collection_name}")
            return vector_store
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """
        Add documents to the vector store with Rate Limiting.
        """
        if not documents:
            logger.warning("No documents provided to add")
            return
        
        # Split documents into chunks
        chunks = self.chunker.split_documents(documents)
        
        if not chunks:
            logger.warning("No chunks created from documents")
            return
        
        # Prepare texts and metadata
        texts = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                'ticker': chunk['ticker'],
                'filing_date': chunk['filing_date'],
                'chunk_id': chunk['chunk_id'],
                'source_file': chunk['source_file']
            }
            for chunk in chunks
        ]
        
        # ---------------------------------------------------------
        # FIX: Batch Processing with Sleep
        # ---------------------------------------------------------
        batch_size = 10
        total_chunks = len(chunks)
        logger.info(f"Starting upload of {total_chunks} chunks in batches of {batch_size}...")

        for i in range(0, total_chunks, batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            try:
                self.vector_store.add_texts(texts=batch_texts, metadatas=batch_metadatas)
                
                # Progress log
                logger.info(f"Processed batch {i // batch_size + 1}/{(total_chunks // batch_size) + 1}")
                
                # CRITICAL: Sleep to prevent "429 Resource Exhausted"
                time.sleep(2.5) 
                
            except Exception as e:
                logger.error(f"Error adding batch {i}: {str(e)}")
                # If rate limit hit, wait longer and retry once
                if "429" in str(e):
                    logger.warning("Hit rate limit. Sleeping 15s before retry...")
                    time.sleep(15)
                    self.vector_store.add_texts(texts=batch_texts, metadatas=batch_metadatas)
                else:
                    raise

        logger.info(f"Successfully added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, k: int = None, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Search for relevant documents using similarity search."""
        k = k or config.TOP_K_RESULTS
        
        # Check if vector store has any documents
        if not self.has_documents():
            logger.warning("Vector store is empty. No documents to search.")
            return []
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search_with_score(
                    query, k=k, filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def search_by_ticker(self, query: str, ticker: str, k: int = None) -> List[Dict]:
        """Search for documents related to a specific ticker."""
        return self.search(query, k=k, filter_dict={'ticker': ticker})
    
    def get_context_for_query(self, query: str, k: int = None) -> str:
        """Get formatted context for a query."""
        # Check if there are any documents first
        if not self.has_documents():
            return "No documents available. Please fetch and index SEC 10-K filings first."
        
        results = self.search(query, k=k)
        
        if not results:
            return "No relevant context found for this query. Try rephrasing or ensure the relevant companies' filings are indexed."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            content = result['content']
            context_parts.append(
                f"[Source {i} - {metadata.get('ticker', 'N/A')} - {metadata.get('filing_date', 'N/A')}]\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store.
        
        Note: Accesses _collection (internal attribute) as ChromaDB doesn't provide
        a public API for getting document count without performing a query.
        """
        try:
            # Access the underlying ChromaDB collection
            # This is necessary as Chroma doesn't expose a public count() method
            collection = self.vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0
    
    def has_documents(self) -> bool:
        """Check if the vector store contains any documents."""
        return self.get_document_count() > 0
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete and recreate the collection
            # Note: Chroma client handling varies by version, this is a safe generic approach
            try:
                self.vector_store.delete_collection()
            except Exception:
                pass
            
            # Reinitialize
            self.vector_store = self._initialize_vector_store()
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            # Fallback for some Chroma versions
            import shutil
            if config.CHROMA_DB_DIR.exists():
                shutil.rmtree(config.CHROMA_DB_DIR)
                config.CHROMA_DB_DIR.mkdir()


def main():
    """Example usage of RAGEngine."""
    rag = RAGEngine()
    
    # Example documents
    sample_docs = [
        {
            'content': 'Apple Inc. reported revenue of $394.3 billion in fiscal year 2022.',
            'ticker': 'AAPL',
            'filing_date': '2022-10-28',
            'file_path': '/path/to/aapl_10k.txt'
        },
        {
            'content': 'Microsoft Corporation achieved $198.3 billion in revenue for fiscal year 2022.',
            'ticker': 'MSFT',
            'filing_date': '2022-07-30',
            'file_path': '/path/to/msft_10k.txt'
        }
    ]
    
    # Add documents
    print("Adding sample documents...")
    rag.add_documents(sample_docs)
    
    # Search
    print("\nSearching for revenue information...")
    results = rag.search("What was the revenue?", k=2)
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Ticker: {result['metadata']['ticker']}")
        print(f"Content: {result['content'][:100]}...")
        print(f"Score: {result['score']:.4f}")


if __name__ == "__main__":
    main()
