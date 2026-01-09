"""
Text Splitter Module

Implements document chunking using LangChain's RecursiveCharacterTextSplitter
for optimal retrieval performance.
"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Handles text splitting for RAG pipeline."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        if not text:
            logger.warning("Empty text provided for splitting")
            return []
        
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        return chunks
    
    def split_documents(self, documents: List[dict]) -> List[dict]:
        """
        Split multiple documents into chunks with metadata.
        
        Args:
            documents: List of document dictionaries with 'content' and metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            chunks = self.split_text(content)
            
            for i, chunk in enumerate(chunks):
                chunk_dict = {
                    'content': chunk,
                    'chunk_id': i,
                    'ticker': doc.get('ticker', 'unknown'),
                    'filing_date': doc.get('filing_date', 'unknown'),
                    'source_file': doc.get('file_path', 'unknown')
                }
                all_chunks.append(chunk_dict)
        
        logger.info(f"Split {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks


def main():
    """Example usage of DocumentChunker."""
    chunker = DocumentChunker()
    
    # Example text
    sample_text = """
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
    
    Revenue for fiscal year 2022 was $394.3 billion, representing a year-over-year increase of 8%.
    
    The company's net income was $99.8 billion for the same period.
    """ * 10
    
    chunks = chunker.split_text(sample_text)
    print(f"Created {len(chunks)} chunks from sample text")
    print(f"First chunk preview: {chunks[0][:100]}...")


if __name__ == "__main__":
    main()
