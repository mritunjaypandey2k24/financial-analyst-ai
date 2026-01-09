"""
Financial Analyst AI Agent Module

Implements an intelligent agent using LangChain and OpenAI to perform
comparative financial analysis using RAG Engine as a tool.
"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialAnalystAgent:
    """
    AI Agent for financial analysis and comparative queries.
    
    Uses RAG Engine to retrieve relevant information from SEC filings
    and provides intelligent responses to financial queries.
    """
    
    def __init__(self, rag_engine):
        """
        Initialize the Financial Analyst Agent.
        
        Args:
            rag_engine: Instance of RAGEngine for document retrieval
        """
        self.rag_engine = rag_engine
        
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Agent will not work properly.")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL,
            temperature=0,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent_executor = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use."""
        tools = [
            Tool(
                name="search_financial_filings",
                func=self._search_filings,
                description=(
                    "Search SEC 10-K financial filings for specific information. "
                    "Input should be a search query about financial data, metrics, or company information. "
                    "Returns relevant excerpts from filings."
                )
            ),
            Tool(
                name="search_ticker_specific",
                func=self._search_by_ticker,
                description=(
                    "Search SEC 10-K filings for a specific company ticker. "
                    "Input should be in format 'ticker:AAPL query:revenue information'. "
                    "Returns relevant excerpts from that company's filings."
                )
            ),
            Tool(
                name="compare_companies",
                func=self._compare_companies,
                description=(
                    "Compare financial information between companies. "
                    "Input should be in format 'ticker1:AAPL ticker2:MSFT query:revenue comparison'. "
                    "Returns relevant information for comparison."
                )
            )
        ]
        
        return tools
    
    def _search_filings(self, query: str) -> str:
        """Search all filings for relevant information."""
        try:
            context = self.rag_engine.get_context_for_query(query, k=5)
            return context
        except Exception as e:
            logger.error(f"Error searching filings: {str(e)}")
            return f"Error searching filings: {str(e)}"
    
    def _search_by_ticker(self, input_str: str) -> str:
        """Search filings for a specific ticker."""
        try:
            # Parse input: "ticker:AAPL query:revenue information"
            parts = input_str.split("query:")
            if len(parts) != 2:
                return "Invalid input format. Use 'ticker:AAPL query:your question'"
            
            ticker_part = parts[0].strip()
            query = parts[1].strip()
            
            ticker = ticker_part.replace("ticker:", "").strip()
            
            results = self.rag_engine.search_by_ticker(query, ticker, k=5)
            
            if not results:
                return f"No information found for ticker {ticker}"
            
            context_parts = []
            for result in results:
                context_parts.append(result['content'])
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error searching by ticker: {str(e)}")
            return f"Error searching by ticker: {str(e)}"
    
    def _compare_companies(self, input_str: str) -> str:
        """Compare information between two companies."""
        try:
            # Parse input: "ticker1:AAPL ticker2:MSFT query:revenue comparison"
            parts = input_str.split("query:")
            if len(parts) != 2:
                return "Invalid input format. Use 'ticker1:AAPL ticker2:MSFT query:your question'"
            
            tickers_part = parts[0].strip()
            query = parts[1].strip()
            
            # Extract tickers
            ticker1 = None
            ticker2 = None
            
            for part in tickers_part.split():
                if part.startswith("ticker1:"):
                    ticker1 = part.replace("ticker1:", "").strip()
                elif part.startswith("ticker2:"):
                    ticker2 = part.replace("ticker2:", "").strip()
            
            if not ticker1 or not ticker2:
                return "Both ticker1 and ticker2 must be provided"
            
            # Search for both tickers
            results1 = self.rag_engine.search_by_ticker(query, ticker1, k=3)
            results2 = self.rag_engine.search_by_ticker(query, ticker2, k=3)
            
            response = f"Information for {ticker1}:\n\n"
            for result in results1:
                response += result['content'] + "\n\n"
            
            response += f"\n\nInformation for {ticker2}:\n\n"
            for result in results2:
                response += result['content'] + "\n\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error comparing companies: {str(e)}")
            return f"Error comparing companies: {str(e)}"
    
    def _create_agent(self):
        """Create the agent executor using LangGraph."""
        system_message = """You are a financial analyst AI assistant specialized in analyzing SEC 10-K filings.
        
Your role is to:
1. Answer questions about company financials based on their SEC 10-K filings
2. Compare financial metrics between different companies
3. Provide accurate, data-driven insights
4. Cite specific information from the filings when possible

When answering:
- Be precise and factual
- Use the search tools to find relevant information from filings
- Compare data points when asked to compare companies
- Explain financial concepts clearly
- Always base your answers on the retrieved filing data

If you don't find specific information in the filings, say so clearly."""

        agent = create_react_agent(
            self.llm, 
            self.tools,
            state_modifier=system_message
        )
        
        return agent
    
    def query(self, question: str) -> str:
        """
        Process a financial analysis query.
        
        Args:
            question: User's question about financial data
            
        Returns:
            Agent's response
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # LangGraph agents use a different invocation pattern
            response = self.agent_executor.invoke({
                "messages": [("user", question)]
            })
            
            # Extract the final message from the agent
            messages = response.get("messages", [])
            if messages:
                # Get the last AI message
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and getattr(msg, 'type', None) == 'ai':
                        return msg.content
                # Fallback: return the last message content
                last_msg = messages[-1]
                return last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            return "I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    def analyze_comparative(self, ticker1: str, ticker2: str, metric: str) -> str:
        """
        Perform comparative analysis between two companies.
        
        Args:
            ticker1: First company ticker
            ticker2: Second company ticker
            metric: Financial metric to compare (e.g., 'revenue', 'profit')
            
        Returns:
            Comparative analysis
        """
        query = f"Compare the {metric} of {ticker1} and {ticker2}. Provide specific numbers and insights."
        return self.query(query)


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
