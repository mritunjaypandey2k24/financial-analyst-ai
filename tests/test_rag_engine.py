"""
Unit tests for the RAG Engine module.
"""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_engine.text_splitter import DocumentChunker


class TestDocumentChunker:
    """Test suite for Document Chunker."""
    
    @pytest.fixture
    def chunker(self):
        """Create a chunker instance."""
        return DocumentChunker(chunk_size=100, chunk_overlap=20)
    
    def test_initialization(self, chunker):
        """Test chunker initialization."""
        assert chunker.chunk_size == 100
        assert chunker.chunk_overlap == 20
        assert chunker.text_splitter is not None
    
    def test_split_text_basic(self, chunker):
        """Test basic text splitting."""
        text = "This is a test. " * 20  # Create a longer text
        
        chunks = chunker.split_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 120 for chunk in chunks)  # Allow some flexibility
    
    def test_split_empty_text(self, chunker):
        """Test splitting empty text."""
        chunks = chunker.split_text("")
        
        assert len(chunks) == 0
    
    def test_split_documents(self, chunker):
        """Test splitting multiple documents."""
        documents = [
            {
                'content': 'Apple Inc. is a technology company. ' * 10,
                'ticker': 'AAPL',
                'filing_date': '2022-10-28',
                'file_path': '/test/path1.txt'
            },
            {
                'content': 'Microsoft Corporation is a software company. ' * 10,
                'ticker': 'MSFT',
                'filing_date': '2022-07-30',
                'file_path': '/test/path2.txt'
            }
        ]
        
        chunks = chunker.split_documents(documents)
        
        assert len(chunks) > 0
        assert all('ticker' in chunk for chunk in chunks)
        assert all('filing_date' in chunk for chunk in chunks)
        assert all('chunk_id' in chunk for chunk in chunks)
        
        # Check that we have chunks from both documents
        tickers = set(chunk['ticker'] for chunk in chunks)
        assert 'AAPL' in tickers
        assert 'MSFT' in tickers
    
    def test_chunk_metadata(self, chunker):
        """Test that chunk metadata is preserved."""
        documents = [
            {
                'content': 'Test content. ' * 20,
                'ticker': 'TEST',
                'filing_date': '2022-01-01',
                'file_path': '/test.txt'
            }
        ]
        
        chunks = chunker.split_documents(documents)
        
        for chunk in chunks:
            assert chunk['ticker'] == 'TEST'
            assert chunk['filing_date'] == '2022-01-01'
            assert chunk['source_file'] == '/test.txt'
            assert 'chunk_id' in chunk
            assert 'content' in chunk


class TestTextSplitting:
    """Test text splitting edge cases."""
    
    def test_small_chunk_size(self):
        """Test with very small chunk size."""
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        text = "This is a test sentence. Another sentence here."
        
        chunks = chunker.split_text(text)
        
        assert len(chunks) > 0
    
    def test_large_chunk_size(self):
        """Test with large chunk size."""
        chunker = DocumentChunker(chunk_size=10000, chunk_overlap=100)
        text = "Short text."
        
        chunks = chunker.split_text(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
