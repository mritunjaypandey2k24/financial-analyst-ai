"""
Tests for agent response extraction and query handling.

These tests specifically validate that the agent properly extracts
responses from LangGraph messages, especially handling tool call
messages vs. final response messages.
"""
import pytest
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.skipif(
    not os.getenv("GOOGLE_AI_STUDIO_API_KEY"),
    reason="Google AI Studio API key required for agent tests"
)
class TestAgentResponse:
    """Test agent response extraction and handling."""
    
    def test_agent_returns_non_empty_response(self, tmp_path):
        """Test that agent.query() returns a non-empty response for valid queries."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        import config
        
        # Setup
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_response"
        rag = RAGEngine(collection_name="test_response_collection")
        
        # Add sample data about Apple revenue
        sample_docs = [
            {
                'content': 'Apple Inc. reported total net sales of $394.3 billion for fiscal year 2022, an increase of 8% year-over-year.',
                'ticker': 'AAPL',
                'filing_date': '2022-10-28',
                'file_path': str(tmp_path / 'aapl.txt')
            },
            {
                'content': 'For the fiscal year ended September 24, 2022, Apple Inc. total revenue was $394,328 million.',
                'ticker': 'AAPL',
                'filing_date': '2022-10-28',
                'file_path': str(tmp_path / 'aapl2.txt')
            }
        ]
        
        rag.add_documents(sample_docs)
        
        # Create agent
        agent = FinancialAnalystAgent(rag)
        
        # Query - this is the exact query from the problem statement
        response = agent.query("What was Apple's revenue in 2022?")
        
        # Assertions
        assert response is not None, "Response should not be None"
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        assert response.strip() != "", "Response should not be just whitespace"
        
        # Response should contain relevant information
        # (at least one of these should be true for a good response)
        has_number = any(char.isdigit() for char in response)
        has_revenue_keyword = any(word in response.lower() for word in ['revenue', 'sales', 'billion', '394'])
        
        assert has_number or has_revenue_keyword, \
            f"Response should contain financial information, got: '{response}'"
    
    def test_agent_handles_no_information_gracefully(self, tmp_path):
        """Test that agent provides meaningful response when information is not available."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        import config
        
        # Setup
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_no_info"
        rag = RAGEngine(collection_name="test_no_info_collection")
        
        # Add sample data about a different topic
        sample_docs = [
            {
                'content': 'Microsoft Corporation operates in various segments including cloud services.',
                'ticker': 'MSFT',
                'filing_date': '2022-07-30',
                'file_path': str(tmp_path / 'msft.txt')
            }
        ]
        
        rag.add_documents(sample_docs)
        
        # Create agent
        agent = FinancialAnalystAgent(rag)
        
        # Query for information that's not in the documents
        response = agent.query("What was Tesla's revenue in 2021?")
        
        # Should still return a non-empty response indicating lack of information
        assert response is not None
        assert len(response) > 0
        assert response.strip() != ""
    
    def test_agent_with_multiple_companies(self, tmp_path):
        """Test agent can handle queries about multiple companies."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        import config
        
        # Setup
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_multi"
        rag = RAGEngine(collection_name="test_multi_collection")
        
        # Add data for multiple companies
        sample_docs = [
            {
                'content': 'Apple Inc. reported revenue of $394.3 billion in 2022.',
                'ticker': 'AAPL',
                'filing_date': '2022-10-28',
                'file_path': str(tmp_path / 'aapl.txt')
            },
            {
                'content': 'Microsoft Corporation reported revenue of $198.3 billion in 2022.',
                'ticker': 'MSFT',
                'filing_date': '2022-07-30',
                'file_path': str(tmp_path / 'msft.txt')
            }
        ]
        
        rag.add_documents(sample_docs)
        
        # Create agent
        agent = FinancialAnalystAgent(rag)
        
        # Query comparing companies
        response = agent.query("Compare Apple and Microsoft revenues in 2022")
        
        # Assertions
        assert response is not None
        assert len(response) > 0
        assert response.strip() != ""
        
        # Response should mention both companies (case insensitive)
        response_lower = response.lower()
        assert 'apple' in response_lower or 'aapl' in response_lower, \
            "Response should mention Apple"
        assert 'microsoft' in response_lower or 'msft' in response_lower, \
            "Response should mention Microsoft"


class TestAgentValidation:
    """Test agent input validation."""
    
    def test_agent_rejects_empty_query(self, tmp_path):
        """Test that agent rejects empty queries."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        import config
        
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_empty"
        rag = RAGEngine(collection_name="test_empty_collection")
        agent = FinancialAnalystAgent(rag)
        
        # Test empty string
        response = agent.query("")
        assert "valid query" in response.lower()
        
        # Test whitespace only
        response = agent.query("   ")
        assert "valid query" in response.lower()
    
    def test_agent_checks_for_documents(self, tmp_path):
        """Test that agent checks if documents are available."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        import config
        
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_no_docs"
        rag = RAGEngine(collection_name="test_no_docs_collection")
        agent = FinancialAnalystAgent(rag)
        
        # Query without adding any documents
        response = agent.query("What is the revenue?")
        assert "no documents" in response.lower() or "fetch and index" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
