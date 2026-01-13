"""
Test script to validate query functionality without SEC access.
Creates mock financial data and tests RAG engine and agent queries.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_engine import RAGEngine
from agent import FinancialAnalystAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_documents():
    """Create mock SEC 10-K filing data for testing."""
    mock_documents = [
        {
            'content': """APPLE INC.
CONSOLIDATED STATEMENTS OF OPERATIONS
(In millions, except number of shares which are reflected in thousands and per share amounts)

                                                    Years ended
                                    September 30,   September 24,   September 25,
                                        2023            2022            2021
Net sales:
Products                           $298,085        $316,199        $297,392
Services                            85,200          78,129          68,425
Total net sales                     383,285         394,328         365,817

Cost of sales:
Products                            189,282         201,471         192,266
Services                             24,855          22,075          20,715
Total cost of sales                 214,137         223,546         212,981

Gross margin                        169,148         170,782         152,836

Operating expenses:
Research and development             29,915          26,251          21,914
Selling, general and administrative  24,932          25,094          21,973
Total operating expenses             54,847          51,345          43,887

Operating income                    114,301         119,437         108,949

Other income/(expense), net           (565)           (334)          258

Income before provision for income taxes  113,736     119,103       109,207

Provision for income taxes            16,741          19,300          14,527

Net income                          $96,995         $99,803         $94,680""",
            'ticker': 'AAPL',
            'filing_date': '2023-10-28',
            'file_path': '/mock/aapl_2023.txt'
        },
        {
            'content': """MICROSOFT CORPORATION
INCOME STATEMENTS
(In millions, except per share amounts)

                                            Year Ended June 30,
                                        2023        2022        2021
Revenue:
  Product                           $75,999     $72,732     $71,074
  Service and other                 135,790     126,013     103,007
    Total revenue                   211,915     198,270     168,088

Cost of revenue:
  Product                            16,338      19,064      18,219
  Service and other                  42,875      43,586      34,013
    Total cost of revenue            59,213      62,650      52,232

Gross margin                        152,702     135,620     115,856

Research and development             27,195      24,512      20,716
Sales and marketing                  21,825      21,825      20,117
General and administrative            5,900       5,900       5,107
  Total operating expenses           54,920      52,237      45,940

Operating income                     97,782      83,383      69,916

Other income, net                     -         -           1,186

Income before income taxes           97,782      83,383      71,102

Provision for income taxes           16,950      16,950      9,831

Net income                          $72,361     $72,738     $61,271""",
            'ticker': 'MSFT',
            'filing_date': '2023-08-03',
            'file_path': '/mock/msft_2023.txt'
        },
        {
            'content': """APPLE INC.
Item 1A. Risk Factors

The Company's business, reputation, results of operations, financial condition and stock price can be affected by a number of factors, whether currently known or unknown, including those described below. When any of these risks actually occurs, the Company's business, reputation, financial condition, results of operations and stock price could be materially and adversely affected.

In addition, the risks described below could materially affect the market price of the Company's common stock.

Global and regional economic conditions, including inflation, interest rates, recession, and credit and financial market volatility and slowdowns, could materially adversely affect the Company's business, results of operations and financial condition.

The Company's operations and performance depend significantly on global and regional economic conditions. Uncertainty about current and future global and regional economic conditions may cause consumers and businesses to postpone purchases in response to tighter credit, unemployment, negative financial news and/or declines in income or asset values, which could have a material negative effect on demand for the Company's products and services.

Additionally, the Company's profitability depends significantly on its ability to offset higher product costs through increased pricing.""",
            'ticker': 'AAPL',
            'filing_date': '2023-10-28',
            'file_path': '/mock/aapl_2023.txt'
        },
        {
            'content': """MICROSOFT CORPORATION
Item 1A. Risk Factors

Our operations and financial results are subject to various risks and uncertainties, including those described below, that could adversely affect our business, financial condition, results of operations, cash flows, and the trading price of our common stock.

STRATEGIC AND COMPETITIVE RISKS

We face intense competition across all markets for our products and services.

Our competitors range from large and established companies to emerging startups and include:
• Companies that provide software, devices, and services primarily focused on productivity and business processes
• Companies that provide cloud-based services
• Companies that provide or have announced intentions to provide AI services and copilots

To compete, we must successfully enact our multi-year digital transformation and cloud-first, AI strategy, continue to bring innovative products and services to market, drive growth in our cloud and AI businesses, and effectively respond to changes in technology and business models.

Security, data protection, and platform abuse

Cyberattacks and security vulnerabilities could lead to reduced revenue, increased costs, liability claims, or harm to our reputation or competitive position.""",
            'ticker': 'MSFT',
            'filing_date': '2023-08-03',
            'file_path': '/mock/msft_2023.txt'
        }
    ]
    
    return mock_documents


def test_rag_engine():
    """Test RAG Engine with mock data."""
    logger.info("=" * 60)
    logger.info("Testing RAG Engine")
    logger.info("=" * 60)
    
    try:
        # Initialize RAG engine
        rag = RAGEngine(collection_name="test_financial_filings")
        
        # Clear any existing data
        logger.info("Clearing existing data...")
        rag.clear_collection()
        
        # Check if empty
        doc_count = rag.get_document_count()
        logger.info(f"Initial document count: {doc_count}")
        
        # Create and add mock documents
        logger.info("Creating mock financial documents...")
        mock_docs = create_mock_documents()
        logger.info(f"Created {len(mock_docs)} mock documents")
        
        # Add documents to RAG engine
        logger.info("Adding documents to RAG engine...")
        rag.add_documents(mock_docs)
        
        # Check document count
        doc_count = rag.get_document_count()
        logger.info(f"Document count after adding: {doc_count}")
        
        if doc_count == 0:
            logger.error("ERROR: No documents were added to vector store!")
            return False
        
        # Test basic search
        logger.info("\nTesting basic search...")
        results = rag.search("revenue", k=3)
        logger.info(f"Search returned {len(results)} results")
        
        if not results:
            logger.error("ERROR: Search returned no results!")
            return False
        
        # Test ticker-specific search
        logger.info("\nTesting ticker-specific search...")
        results = rag.search_by_ticker("revenue", "AAPL", k=2)
        logger.info(f"Ticker-specific search returned {len(results)} results")
        
        if not results:
            logger.error("ERROR: Ticker-specific search returned no results!")
            return False
        
        logger.info("\n✅ RAG Engine tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_queries():
    """Test Financial Analyst Agent with different query types."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Financial Analyst Agent")
    logger.info("=" * 60)
    
    try:
        # Initialize RAG engine and agent
        logger.info("Initializing RAG engine and agent...")
        rag = RAGEngine(collection_name="test_financial_filings")
        agent = FinancialAnalystAgent(rag)
        
        # Ensure we have documents
        if not rag.has_documents():
            logger.error("ERROR: No documents in RAG engine. Run test_rag_engine first.")
            return False
        
        # Test queries
        test_queries = [
            "What was Apple's revenue in 2023?",
            "What was Microsoft's revenue in fiscal year 2023?",
            "Compare AAPL and MSFT revenues",
            "What are the main risk factors for Microsoft?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Test Query {i}: {query}")
            logger.info(f"{'='*60}")
            
            try:
                response = agent.query(query)
                logger.info(f"\nResponse:\n{response}")
                
                # Basic validation
                if not response or len(response) < 10:
                    logger.warning(f"⚠️ Query {i} returned very short response: '{response}'")
                elif "error" in response.lower() and "processing query" in response.lower():
                    logger.error(f"❌ Query {i} returned an error: {response}")
                    return False
                else:
                    logger.info(f"✅ Query {i} completed successfully")
                
                # Add delay between queries to avoid rate limits
                import time
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Query {i} failed with exception: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        logger.info("\n✅ All agent query tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "FINANCIAL ANALYST AI - QUERY TEST" + " " * 14 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    # Test RAG Engine
    rag_success = test_rag_engine()
    
    if not rag_success:
        logger.error("\n❌ RAG Engine tests failed. Stopping here.")
        return 1
    
    # Test Agent Queries
    agent_success = test_agent_queries()
    
    if not agent_success:
        logger.error("\n❌ Agent tests failed.")
        return 1
    
    logger.info("\n" + "=" * 60)
    logger.info("ALL TESTS PASSED! ✅")
    logger.info("=" * 60)
    logger.info("\nThe query system is working correctly with mock data.")
    logger.info("In production, it will fetch real SEC 10-K filings and answer queries about them.")
    
    return 0


if __name__ == "__main__":
    exit(main())
