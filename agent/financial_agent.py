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
    
    # Rate limiting configuration constants
    MAX_RETRIES = 3
    BASE_WAIT_TIME = 60  # seconds, increased from 15s
    MIN_WAIT_BETWEEN_CALLS = 10  # seconds, proactive rate limiting
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        
        if not config.GOOGLE_AI_STUDIO_API_KEY:
            logger.warning("GOOGLE_AI_STUDIO_API_KEY not set. Agent will not work properly.")
        
        # Initialize LLM with strict parameters for Free Tier
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0,
            google_api_key=config.GOOGLE_AI_STUDIO_API_KEY,
            # We handle retries manually for better control over rate limits
            max_retries=0,  # Disable internal retries, we handle it ourselves
            request_timeout=90  # Longer timeout for free tier
        )
        
        # Track last API call time for rate limiting
        self.last_api_call_time = 0
        
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use."""
        tools = [
            Tool(
                name="search_financial_filings",
                func=self._search_filings,
                description=(
                    "Search across all indexed SEC 10-K financial filings for information. "
                    "Use this for general financial queries or when no specific company is mentioned. "
                    "Input: A natural language query about financial data (e.g., 'revenue', 'profit', 'expenses'). "
                    "Returns: Relevant excerpts from 10-K filings with company names and dates."
                )
            ),
            Tool(
                name="search_ticker_specific",
                func=self._search_by_ticker,
                description=(
                    "Search filings for a SPECIFIC company using its ticker symbol. "
                    "Use this when the query mentions a specific company name or you need data for one company. "
                    "Input format: 'ticker:SYMBOL query:your question' (e.g., 'ticker:AAPL query:revenue in 2022'). "
                    "Common tickers: AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon). "
                    "Returns: Company-specific financial information from their 10-K filings."
                )
            ),
            Tool(
                name="compare_companies",
                func=self._compare_companies,
                description=(
                    "Compare financial data between TWO companies. "
                    "Use this when the query asks to compare, contrast, or show differences between companies. "
                    "Input format: 'ticker1:SYMBOL1 ticker2:SYMBOL2 query:what to compare' "
                    "(e.g., 'ticker1:AAPL ticker2:MSFT query:revenue comparison in 2022'). "
                    "Returns: Side-by-side financial data for both companies."
                )
            )
        ]
        return tools
    
    def _search_filings(self, query: str) -> str:
        """Search SEC filings for information."""
        try:
            # Check if RAG engine has documents
            if not self.rag_engine.has_documents():
                return "No documents available. Please fetch and index SEC 10-K filings first before querying."
            
            # Lower k to 2 to save tokens and avoid limits (reduced from 3)
            context = self.rag_engine.get_context_for_query(query, k=2)
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
            
            results = self.rag_engine.search_by_ticker(query, ticker, k=2)  # Reduced from 3
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
            
            # Very conservative search to avoid token limits (reduced to k=1)
            results1 = self.rag_engine.search_by_ticker(query, tickers[0], k=1)
            results2 = self.rag_engine.search_by_ticker(query, tickers[1], k=1)
            
            if not results1 and not results2:
                return f"No information found for {tickers[0]} or {tickers[1]}. Ensure these companies' filings are indexed."
            elif not results1:
                return f"No information found for {tickers[0]}. Only {tickers[1]} data is available."
            elif not results2:
                return f"No information found for {tickers[1]}. Only {tickers[0]} data is available."
            
            # Format results properly as strings
            data1 = "\n".join([r['content'] for r in results1]) if results1 else ""
            data2 = "\n".join([r['content'] for r in results2]) if results2 else ""
            
            return f"Data for {tickers[0]}:\n{data1}\n\nData for {tickers[1]}:\n{data2}"
        except Exception as e:
            logger.error(f"Error in _compare_companies: {str(e)}")
            return f"Error comparing companies: {str(e)}"
    
    def _create_agent(self):
        system_message = """You are a financial analyst assistant specializing in SEC 10-K filings analysis. When answering questions:

1. **Use the Tools**: Always use the available tools to search SEC 10-K filings for relevant information.
   - Use 'search_financial_filings' for general queries
   - Use 'search_ticker_specific' when the query is about a specific company
   - Use 'compare_companies' when comparing two companies

2. **Extract Key Information**: After gathering information, identify:
   - Specific financial figures (revenue, income, expenses, etc.)
   - Time periods (fiscal year, quarter)
   - Companies mentioned (ticker symbols)
   - Percentage changes or growth rates

3. **Provide Clear Answers**: 
   - Answer directly with specific numbers and dates
   - Include context (e.g., "Apple's revenue in fiscal year 2022 was $394.3 billion")
   - Cite the source company and filing date when available
   - Use clear formatting (bullet points for multiple facts)

4. **Handle Missing Information**:
   - If information is not found, explicitly state what is missing
   - Suggest alternative queries or companies that might have relevant data
   - Never make up financial data

5. **Always Provide a Final Answer**: 
   - After using tools, always synthesize the information into a clear, final response
   - Do not just return raw search results

Remember: Users expect precise financial data with proper attribution to source documents."""
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
        
        # Preprocess query to add helpful context
        enhanced_question = self._enhance_query(question)
        logger.debug(f"Original query: {question}")
        logger.debug(f"Enhanced query: {enhanced_question}")
        
        # Rate limiting error patterns to detect
        rate_limit_errors = ["429", "resource_exhausted", "quota", "rate limit"]
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Add rate limiting - wait before each attempt to avoid hitting limits
                current_time = time.time()
                time_since_last_call = current_time - self.last_api_call_time
                
                if time_since_last_call < self.MIN_WAIT_BETWEEN_CALLS:
                    wait_time = self.MIN_WAIT_BETWEEN_CALLS - time_since_last_call
                    logger.info(f"Rate limiting: waiting {wait_time:.1f}s before attempt...")
                    time.sleep(wait_time)
                
                logger.info(f"Processing query (Attempt {attempt+1}/{self.MAX_RETRIES})...")
                self.last_api_call_time = time.time()
                
                response = self.agent_executor.invoke({"messages": [("user", enhanced_question)]})
                
                # Extract response - find the last AI message with actual content
                messages = response.get("messages", [])
                logger.debug(f"Received {len(messages)} messages from agent")
                
                if messages:
                    # Iterate through messages in reverse to find the final AI response
                    for msg in reversed(messages):
                        if getattr(msg, 'type', None) == 'ai':
                            # Check if this message has content and is not just a tool call
                            content = msg.content
                            tool_calls = getattr(msg, 'tool_calls', [])
                            
                            # Log for debugging
                            logger.debug(f"Found AI message - content length: {len(str(content))}, tool_calls: {len(tool_calls)}")
                            
                            # Return the first AI message with actual content
                            # (iterating backwards, so this is the last AI message)
                            if content and str(content).strip():
                                logger.info(f"Returning response with {len(str(content))} characters")
                                return str(content)
                    
                    # Fallback: if no AI message with content found, return error
                    logger.warning("No AI message with content found in response")
                    return "I processed your query but couldn't generate a response. Please try rephrasing your question. Helpful tip: Include the company name or ticker symbol (e.g., 'Apple' or 'AAPL') and specific metric (e.g., 'revenue', 'net income') in your query."
                
                logger.warning("No messages in agent response")
                return "No response generated. Please try rephrasing your question with more specific details."

            except Exception as e:
                error_msg = str(e).lower()
                # Catch the specific Google "Speed Limit" errors
                if any(pattern in error_msg for pattern in rate_limit_errors):
                    # Exponential backoff: wait longer with each retry
                    wait_time = self.BASE_WAIT_TIME * (2 ** attempt)  # 60s, 120s, 240s
                    logger.warning(f"⚠️ Hit Rate Limit on attempt {attempt + 1}/{self.MAX_RETRIES}")
                    print(f"⚠️ Hit Speed Limit. Pausing for {wait_time} seconds to let cool down...")
                    time.sleep(wait_time)
                    continue # Try again
                else:
                    logger.error(f"Error: {e}")
                    return f"Error processing query: {str(e)}. Please ensure your question includes specific company names and financial metrics."
        
        # If all retries failed due to rate limits
        return "The Google AI API is currently rate-limited. This is common with the free tier when making multiple requests. Please wait 2-3 minutes before trying again. Consider simplifying your query to use fewer API calls."
    
    def _enhance_query(self, question: str) -> str:
        """
        Enhance the query with additional context to improve retrieval.
        
        This method adds context hints to help the agent better understand
        what information to look for in the financial filings.
        """
        # Convert to lowercase for pattern matching
        q_lower = question.lower()
        
        # Add context for common financial terms
        enhancements = []
        
        # Detect if it's a comparative query
        if any(word in q_lower for word in ['compare', 'versus', 'vs', 'difference', 'better']):
            enhancements.append("(This is a comparison question)")
        
        # Detect specific metrics mentioned
        metrics = []
        if 'revenue' in q_lower or 'sales' in q_lower:
            metrics.append('revenue')
        if 'profit' in q_lower or 'income' in q_lower or 'earnings' in q_lower:
            metrics.append('net income')
        if 'expense' in q_lower or 'cost' in q_lower:
            metrics.append('expenses')
        if 'margin' in q_lower:
            metrics.append('profit margins')
        if 'asset' in q_lower:
            metrics.append('assets')
        if 'liability' in q_lower or 'debt' in q_lower:
            metrics.append('liabilities')
        
        if metrics:
            enhancements.append(f"Metrics: {', '.join(metrics)}")
        
        # Detect time period
        if 'fiscal year' in q_lower or 'fy' in q_lower or any(str(year) in q_lower for year in range(2018, 2026)):
            enhancements.append("(Looking for annual fiscal year data)")
        elif 'quarter' in q_lower or 'q1' in q_lower or 'q2' in q_lower or 'q3' in q_lower or 'q4' in q_lower:
            enhancements.append("(Looking for quarterly data)")
        
        # Return enhanced query if we found enhancements, otherwise return original
        if enhancements:
            return f"{question} {' '.join(enhancements)}"
        return question

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
