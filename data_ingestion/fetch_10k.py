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
        
        # ---------------------------------------------------------
        # FIX: Parse User-Agent from config instead of hardcoding it
        # ---------------------------------------------------------
        user_agent = config.USER_AGENT
        
        # Parse the user agent string
        try:
            # Support "Name <email>" format (Standard)
            if '<' in user_agent and '>' in user_agent:
                # Split on first '<' to handle edge cases
                parts = user_agent.split('<', 1)
                company = parts[0].strip()
                # Extract email between < and >
                email = parts[1].split('>')[0].strip()
            # Support "Name email" format (Legacy)
            elif ' ' in user_agent:
                company, email = user_agent.rsplit(' ', 1)
            else:
                raise ValueError("Could not parse user agent")
                
            if not company or not email or '@' not in email:
                raise ValueError("Invalid company or email format")
        except Exception as e:
            logger.error(f"Failed to parse USER_AGENT from .env: {user_agent}")
            raise ValueError("Invalid USER_AGENT in .env. Format should be: Name <email@domain.com>")
        
        # Initialize the SEC downloader
        try:
            logger.info(f"Initializing SEC Downloader with: {company} | {email}")
            self.downloader = Downloader(
                company, 
                email, 
                str(self.data_dir)
            )
        except Exception as e:
            logger.error(f"Failed to initialize SEC Downloader: {str(e)}")
            # Re-raise the actual error instead of masking it
            raise
        
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
            count = self.downloader.get("10-K", ticker, limit=num_filings)
            
            if count == 0:
                logger.warning(f"No filings found for {ticker}")
                return []
            
            # Get the downloaded files
            ticker_dir = self.data_dir / "sec-edgar-filings" / ticker / "10-K"
            filings = []
            
            if ticker_dir.exists():
                # Process the most recent folders first
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
        """
        try:
            # 1. Look for full-submission.txt (standard in recent downloader versions)
            filing_file = filing_dir / "full-submission.txt"
            
            # 2. Fallback: Search for any .txt file if standard one is missing
            if not filing_file.exists():
                txt_files = list(filing_dir.glob("*.txt"))
                if txt_files:
                    filing_file = txt_files[0]
                else:
                    logger.warning(f"No filing text file found in {filing_dir}")
                    return None
            
            # Read content
            with open(filing_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract clean text if it looks like HTML
            if "<html>" in content.lower() or "<HTML>" in content:
                text_content = self._extract_text_from_html(content)
            else:
                text_content = content
            
            filing_info = {
                'ticker': ticker,
                'filing_date': filing_dir.name, # Using folder name (accession number) as ID
                'file_path': str(filing_file),
                'content': text_content,
                'raw_content': content[:1000] # Store snippet only to save memory
            }
            
            return filing_info
            
        except Exception as e:
            logger.error(f"Error processing filing directory {filing_dir}: {str(e)}")
            return None
    
    def _extract_text_from_html(self, content: str) -> str:
        """Extract plain text from HTML content."""
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text with separator
            text = soup.get_text(separator=' ', strip=True)
            return text
            
        except Exception as e:
            logger.warning(f"Error extracting text from HTML: {str(e)}")
            return content
    
    def fetch_multiple_tickers(self, tickers: List[str], num_filings: int = 1) -> Dict[str, List[Dict[str, str]]]:
        """Fetch 10-K filings for multiple tickers."""
        results = {}
        for ticker in tickers:
            filings = self.fetch_10k_filing(ticker, num_filings)
            results[ticker] = filings
        return results

if __name__ == "__main__":
    # Simple test
    fetcher = SECFilingFetcher()
    print("Fetching AAPL 10-K filing...")
    filings = fetcher.fetch_10k_filing("AAPL", num_filings=1)
    if filings:
        print(f"Success! Content length: {len(filings[0]['content'])}")
    else:
        print("Failed.")