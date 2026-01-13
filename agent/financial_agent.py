"""
Financial Analyst AI Agent Module

Implements an intelligent agent using LangChain and Google AI Studio to perform
comparative financial analysis using RAG Engine as a tool.
"""
from typing import List, Dict, Optional
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialAnalystAgent:
    """
    AI Agent for financial analysis and comparative queries.
    """
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        
        if not config.GOOGLE_AI_STUDIO_API_KEY:
            logger.warning("GOOGLE_AI_STUDIO_API_KEY not set. Agent will not work properly.")
        
        # Initialize LLM with strict parameters for Free Tier
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0,
            google_api_key=config.GOOGLE_AI_STUDIO_API_KEY,
            # We handle retries manually for better control over the 15s wait
            max_retries=1, 
            request_timeout=60
        )
        
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use."""
        tools = [
            Tool(
                name="search_financial_filings",
                func=self._search_filings,
                description="Search SEC 10-K financial filings. Input: a query about financial data."
            ),
            Tool(
                name="search_ticker_specific",
                func=self._search_by_ticker,
                description="Search filings for a specific company. Input format: 'ticker:AAPL query:revenue'"
            ),
            Tool(
                name="compare_companies",
                func=self._compare_companies,
                description="Compare two companies. Input format: 'ticker1:AAPL ticker2:MSFT query:revenue comparison'"
            )
        ]
        return tools
    
    def _search_filings(self, query: str) -> str:
        """Search SEC filings for information."""
        try:
            # Check if RAG engine has documents
            if not self.rag_engine.has_documents():
                return "No documents available. Please fetch and index SEC 10-K filings first before querying."
            
            # Lower k to 3 to save tokens and avoid limits
            context = self.rag_engine.get_context_for_query(query, k=3)
            return context
        except Exception as e:
            logger.error(f"Error in _search_filings: {str(e)}")
            return f"Error searching filings: {str(e)}"
    
    def _search_by_ticker(self, input_str: str) -> str:
        """Search filings for a specific company ticker."""
        try:
            # Check if RAG engine has documents
            if not self.rag_engine.has_documents():
                return "No documents available. Please fetch and index SEC 10-K filings first before querying."
            
            if "query:" not in input_str:
                return "Invalid format. Use 'ticker:AAPL query:your question'"
            
            parts = input_str.split("query:")
            ticker = parts[0].replace("ticker:", "").strip()
            query = parts[1].strip()
            
            results = self.rag_engine.search_by_ticker(query, ticker, k=3)
            if not results:
                return f"No information found for {ticker}. Ensure this company's filings are indexed."
            
            return "\n\n".join([r['content'] for r in results])
        except Exception as e:
            logger.error(f"Error in _search_by_ticker: {str(e)}")
            return f"Error searching for ticker: {str(e)}"
    
    def _compare_companies(self, input_str: str) -> str:
        """Compare data between two companies."""
        try:
            # Check if RAG engine has documents
            if not self.rag_engine.has_documents():
                return "No documents available. Please fetch and index SEC 10-K filings first before comparing companies."
            
            if "query:" not in input_str:
                return "Invalid format. Expected 'ticker1:AAPL ticker2:MSFT query:revenue comparison'"
            
            query = input_str.split("query:")[1].strip()
            words = input_str.split()
            tickers = [w.split(':')[1] for w in words if ':' in w and 'ticker' in w]
            
            if len(tickers) < 2:
                return "Need at least two tickers to compare. Format: 'ticker1:AAPL ticker2:MSFT query:your question'"
            
            # Very conservative search to avoid token limits
            results1 = self.rag_engine.search_by_ticker(query, tickers[0], k=2)
            results2 = self.rag_engine.search_by_ticker(query, tickers[1], k=2)
            
            if not results1 and not results2:
                return f"No information found for {tickers[0]} or {tickers[1]}. Ensure these companies' filings are indexed."
            elif not results1:
                return f"No information found for {tickers[0]}. Only {tickers[1]} data is available."
            elif not results2:
                return f"No information found for {tickers[1]}. Only {tickers[0]} data is available."
            
            return f"Data for {tickers[0]}:\n{results1}\n\nData for {tickers[1]}:\n{results2}"
        except Exception as e:
            logger.error(f"Error in _compare_companies: {str(e)}")
            return f"Error comparing companies: {str(e)}"
    
    def _create_agent(self):
        system_message = "You are a financial analyst. Use the tools to find info in SEC filings. If you cannot find info, say so."
        return create_react_agent(self.llm, self.tools, prompt=system_message)
    
    def query(self, question: str) -> str:
        """Process a query with validation and error handling."""
        # Input validation
        if not question or not question.strip():
            return "Please provide a valid query."
        
        question = question.strip()
        
        # Check if RAG engine has documents before attempting query
        if not self.rag_engine.has_documents():
            return "No documents available in the system. Please fetch and index SEC 10-K filings first before asking questions."
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Processing query (Attempt {attempt+1}/{max_retries})...")
                
                response = self.agent_executor.invoke({"messages": [("user", question)]})
                
                # Extract response
                messages = response.get("messages", [])
                if messages:
                    for msg in reversed(messages):
                        if getattr(msg, 'type', None) == 'ai':
                            return msg.content
                    return str(messages[-1].content)
                return "No response generated."

            except Exception as e:
                error_msg = str(e).lower()
                # Catch the specific Google "Speed Limit" errors
                if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
                    print(f"⚠️ Hit Speed Limit. Pausing for 15 seconds to let cool down...")
                    time.sleep(15)  # The magic fix: Wait longer than the error suggests
                    continue # Try again
                else:
                    logger.error(f"Error: {e}")
                    return f"Error: {str(e)}"
        
        return "I am currently overloaded with requests. Please wait 1 minute and try again."

def main():
    """Example usage of FinancialAnalystAgent."""
    from rag_engine import RAGEngine
    
    # Initialize RAG engine
    rag = RAGEngine()
    
    # Create sample documents
    sample_docs = [
        {
            'content': 'Apple Inc. reported total net sales of $394.3 billion for fiscal year 2022, an increase of 8% year-over-year.',
            'ticker': 'AAPL',
            'filing_date': '2022-10-28',
            'file_path': '/path/to/aapl_10k.txt'
        },
        {
            'content': 'Microsoft Corporation reported revenue of $198.3 billion in fiscal year 2022, an increase of 18% compared to fiscal year 2021.',
            'ticker': 'MSFT',
            'filing_date': '2022-07-30',
            'file_path': '/path/to/msft_10k.txt'
        }
    ]
    
    print("Adding sample documents to RAG engine...")
    rag.add_documents(sample_docs)
    
    # Initialize agent
    print("\nInitializing Financial Analyst Agent...")
    agent = FinancialAnalystAgent(rag)
    
    # Example queries
    print("\n" + "="*50)
    print("Query: What was Apple's revenue in 2022?")
    print("="*50)
    response = agent.query("What was Apple's revenue in 2022?")
    print(f"\nResponse: {response}")
    
    print("\n" + "="*50)
    print("Query: Compare Apple and Microsoft revenues in 2022")
    print("="*50)
    response = agent.query("Compare Apple and Microsoft revenues in 2022")
    print(f"\nResponse: {response}")


if __name__ == "__main__":
    main()
