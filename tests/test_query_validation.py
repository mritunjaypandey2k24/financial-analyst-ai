"""
Unit tests for query validation and error handling.

This test suite validates the fixes for the query error issue:
1. Document existence checks
2. Query input validation
3. Error handling in agent and RAG engine
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRAGEngineValidation:
    """Test document validation in RAG Engine."""
    
    def test_has_documents_empty_store(self):
        """Test has_documents returns False for empty store."""
        from rag_engine import RAGEngine
        
        # Mock the vector store to return 0 count
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            assert not rag.has_documents()
    
    def test_has_documents_with_data(self):
        """Test has_documents returns True when documents exist."""
        from rag_engine import RAGEngine
        
        # Mock the vector store to return positive count
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            assert rag.has_documents()
    
    def test_get_document_count(self):
        """Test get_document_count returns correct count."""
        from rag_engine import RAGEngine
        
        # Mock the vector store
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 10
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            assert rag.get_document_count() == 10
    
    def test_search_empty_store(self):
        """Test search returns empty list when store is empty."""
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            results = rag.search("test query")
            assert results == []
    
    def test_get_context_empty_store(self):
        """Test get_context_for_query returns helpful message for empty store."""
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            context = rag.get_context_for_query("test query")
            assert "No documents available" in context
            assert "fetch and index" in context.lower()


class TestAgentValidation:
    """Test query validation in Financial Agent."""
    
    def test_query_with_empty_input(self):
        """Test agent rejects empty query."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            # Mock the LLM to avoid API calls
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Test empty string
                response = agent.query("")
                assert "valid query" in response.lower()
                
                # Test whitespace only
                response = agent.query("   ")
                assert "valid query" in response.lower()
    
    def test_query_with_no_documents(self):
        """Test agent rejects query when no documents are indexed."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0  # No documents
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                response = agent.query("What was Apple's revenue?")
                assert "No documents available" in response
                assert "fetch and index" in response.lower()
    
    def test_search_filings_with_empty_store(self):
        """Test _search_filings returns helpful message for empty store."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                result = agent._search_filings("test query")
                assert "No documents available" in result
    
    def test_search_by_ticker_with_empty_store(self):
        """Test _search_by_ticker returns helpful message for empty store."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                result = agent._search_by_ticker("ticker:AAPL query:revenue")
                assert "No documents available" in result
    
    def test_compare_companies_with_empty_store(self):
        """Test _compare_companies returns helpful message for empty store."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 0
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                result = agent._compare_companies("ticker1:AAPL ticker2:MSFT query:revenue")
                assert "No documents available" in result


class TestErrorHandling:
    """Test error handling improvements."""
    
    def test_search_by_ticker_invalid_format(self):
        """Test _search_by_ticker handles invalid input format."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Invalid format - missing "query:"
                result = agent._search_by_ticker("ticker:AAPL revenue")
                assert "Invalid format" in result
    
    def test_compare_companies_invalid_format(self):
        """Test _compare_companies handles invalid input format."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Invalid format - missing "query:"
                result = agent._compare_companies("ticker1:AAPL ticker2:MSFT revenue")
                assert "Invalid format" in result
                
                # Invalid format - only one ticker
                result = agent._compare_companies("ticker1:AAPL query:revenue")
                assert "two tickers" in result.lower()
    
    def test_get_document_count_error_handling(self):
        """Test get_document_count handles errors gracefully."""
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_store._collection.count.side_effect = Exception("Database error")
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            count = rag.get_document_count()
            assert count == 0  # Should return 0 on error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
