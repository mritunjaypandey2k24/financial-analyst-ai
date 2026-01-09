"""
SEC 10-K Filing Fetcher Module

This module provides functionality to fetch and parse SEC 10-K filings
from the EDGAR database for financial analysis.
"""
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict
import requests
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECFilingFetcher:
    """Fetches and processes SEC 10-K filings from EDGAR database."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the SEC Filing Fetcher.
        
        Args:
            data_dir: Directory to store downloaded filings. Defaults to config.DATA_DIR
        """
        self.data_dir = data_dir or config.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = Downloader("FinancialAnalystAI", "research@example.com", str(self.data_dir))
        
    def fetch_10k_filing(self, ticker: str, num_filings: int = 1) -> List[Dict[str, str]]:
        """
        Fetch 10-K filings for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            num_filings: Number of recent filings to fetch
            
        Returns:
            List of dictionaries containing filing information
        """
        logger.info(f"Fetching {num_filings} 10-K filing(s) for {ticker}")
        
        try:
            # Download 10-K filings
            self.downloader.get("10-K", ticker, amount=num_filings)
            
            # Get the downloaded files
            ticker_dir = self.data_dir / "sec-edgar-filings" / ticker / "10-K"
            filings = []
            
            if ticker_dir.exists():
                for filing_dir in sorted(ticker_dir.iterdir(), reverse=True)[:num_filings]:
                    if filing_dir.is_dir():
                        filing_info = self._process_filing_directory(ticker, filing_dir)
                        if filing_info:
                            filings.append(filing_info)
            
            logger.info(f"Successfully fetched {len(filings)} filing(s) for {ticker}")
            return filings
            
        except Exception as e:
            logger.error(f"Error fetching 10-K for {ticker}: {str(e)}")
            return []
    
    def _process_filing_directory(self, ticker: str, filing_dir: Path) -> Optional[Dict[str, str]]:
        """
        Process a single filing directory and extract text content.
        
        Args:
            ticker: Stock ticker symbol
            filing_dir: Path to the filing directory
            
        Returns:
            Dictionary with filing information or None if processing fails
        """
        try:
            # Look for the main filing document
            filing_file = None
            for file in filing_dir.glob("*.txt"):
                if "full-submission" in file.name:
                    filing_file = file
                    break
            
            if not filing_file:
                # Try to find any .txt file
                txt_files = list(filing_dir.glob("*.txt"))
                if txt_files:
                    filing_file = txt_files[0]
            
            if not filing_file:
                logger.warning(f"No filing document found in {filing_dir}")
                return None
            
            # Read and parse the filing content
            with open(filing_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract text from HTML if present
            text_content = self._extract_text_from_html(content)
            
            filing_info = {
                'ticker': ticker,
                'filing_date': filing_dir.name,
                'file_path': str(filing_file),
                'content': text_content,
                'raw_content': content
            }
            
            return filing_info
            
        except Exception as e:
            logger.error(f"Error processing filing directory {filing_dir}: {str(e)}")
            return None
    
    def _extract_text_from_html(self, content: str) -> str:
        """
        Extract plain text from HTML content.
        
        Args:
            content: Raw HTML content
            
        Returns:
            Extracted plain text
        """
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"Error extracting text from HTML: {str(e)}")
            return content
    
    def fetch_multiple_tickers(self, tickers: List[str], num_filings: int = 1) -> Dict[str, List[Dict[str, str]]]:
        """
        Fetch 10-K filings for multiple tickers.
        
        Args:
            tickers: List of stock ticker symbols
            num_filings: Number of recent filings to fetch per ticker
            
        Returns:
            Dictionary mapping tickers to their filing information
        """
        results = {}
        
        for ticker in tickers:
            filings = self.fetch_10k_filing(ticker, num_filings)
            results[ticker] = filings
        
        return results
    
    def get_filing_text(self, ticker: str, filing_index: int = 0) -> Optional[str]:
        """
        Get the text content of a specific filing.
        
        Args:
            ticker: Stock ticker symbol
            filing_index: Index of the filing (0 = most recent)
            
        Returns:
            Text content of the filing or None if not found
        """
        filings = self.fetch_10k_filing(ticker, filing_index + 1)
        
        if filings and len(filings) > filing_index:
            return filings[filing_index]['content']
        
        return None


def main():
    """Example usage of the SECFilingFetcher."""
    fetcher = SECFilingFetcher()
    
    # Fetch 10-K for Apple
    print("Fetching AAPL 10-K filing...")
    filings = fetcher.fetch_10k_filing("AAPL", num_filings=1)
    
    if filings:
        print(f"Successfully fetched {len(filings)} filing(s)")
        print(f"Filing date: {filings[0]['filing_date']}")
        print(f"Content length: {len(filings[0]['content'])} characters")
    else:
        print("Failed to fetch filings")


if __name__ == "__main__":
    main()
