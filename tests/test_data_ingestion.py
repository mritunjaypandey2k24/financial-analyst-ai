"""
Unit tests for the Data Ingestion module.
"""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_ingestion.fetch_10k import SECFilingFetcher


class TestSECFilingFetcher:
    """Test suite for SEC Filing Fetcher."""
    
    @pytest.fixture
    def fetcher(self, tmp_path):
        """Create a fetcher instance with temporary directory."""
        return SECFilingFetcher(data_dir=tmp_path)
    
    def test_initialization(self, fetcher, tmp_path):
        """Test fetcher initialization."""
        assert fetcher.data_dir == tmp_path
        assert fetcher.data_dir.exists()
        assert fetcher.downloader is not None
    
    def test_extract_text_from_html(self, fetcher):
        """Test HTML text extraction."""
        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <p>Apple Inc. revenue was $100 billion.</p>
            <script>console.log('test');</script>
        </body>
        </html>
        """
        
        text = fetcher._extract_text_from_html(html_content)
        
        assert "Apple Inc." in text
        assert "revenue" in text
        assert "console.log" not in text  # Scripts should be removed
    
    def test_extract_text_from_plain_text(self, fetcher):
        """Test extraction from plain text."""
        plain_text = "This is plain text content."
        
        result = fetcher._extract_text_from_html(plain_text)
        
        assert "plain text content" in result
    
    def test_get_filing_text_not_found(self, fetcher):
        """Test getting text for non-existent filing."""
        result = fetcher.get_filing_text("NONEXISTENT", 0)
        
        assert result is None


class TestFilingParser:
    """Test filing parsing functionality."""
    
    def test_html_cleanup(self):
        """Test that HTML is properly cleaned."""
        from data_ingestion.fetch_10k import SECFilingFetcher
        
        fetcher = SECFilingFetcher()
        html = "<p>Test   content\n\nwith   spaces</p>"
        
        result = fetcher._extract_text_from_html(html)
        
        # Should clean up extra whitespace
        assert "Test" in result
        assert "content" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
