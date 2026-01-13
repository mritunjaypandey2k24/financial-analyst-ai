"""
Tests for query enhancement and improved context retrieval.

This test suite validates the improvements made to address the query processing issue.
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestQueryEnhancement:
    """Test query enhancement functionality."""
    
    def test_enhance_query_with_metrics(self):
        """Test that queries with financial metrics are enhanced."""
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
                
                # Test revenue query enhancement
                enhanced = agent._enhance_query("What was Apple's revenue in 2022?")
                assert 'revenue' in enhanced.lower()
                assert '2022' in enhanced
                
                # Test comparison query enhancement
                enhanced = agent._enhance_query("Compare AAPL and MSFT")
                assert 'comparison' in enhanced.lower() or 'compare' in enhanced.lower()
    
    def test_enhance_query_with_time_period(self):
        """Test that queries with time periods are enhanced."""
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
                
                # Test fiscal year detection
                enhanced = agent._enhance_query("Apple revenue fiscal year 2022")
                assert 'fiscal year' in enhanced.lower() or 'annual' in enhanced.lower()
    
    def test_enhance_query_no_changes_needed(self):
        """Test that simple queries without special patterns are returned unchanged."""
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
                
                # Test simple query
                simple_query = "Tell me about AAPL"
                enhanced = agent._enhance_query(simple_query)
                # Should be returned as-is or with minimal changes
                assert 'AAPL' in enhanced


class TestImprovedContextRetrieval:
    """Test improved context formatting."""
    
    def test_context_includes_relevance_score(self):
        """Test that formatted context includes relevance scores."""
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            
            # Mock search results with scores
            mock_store.similarity_search_with_score.return_value = [
                (Mock(page_content="Apple revenue was $394B", metadata={'ticker': 'AAPL', 'filing_date': '2022-10-28'}), 0.15),
            ]
            
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            context = rag.get_context_for_query("revenue")
            
            # Check that context is formatted properly
            assert 'AAPL' in context
            assert '2022-10-28' in context
            assert 'Relevance' in context
    
    def test_context_formatting_with_separators(self):
        """Test that context uses clear separators between results."""
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            
            # Mock multiple search results
            mock_store.similarity_search_with_score.return_value = [
                (Mock(page_content="First result", metadata={'ticker': 'AAPL', 'filing_date': '2022'}), 0.1),
                (Mock(page_content="Second result", metadata={'ticker': 'MSFT', 'filing_date': '2022'}), 0.2),
            ]
            
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            context = rag.get_context_for_query("test")
            
            # Check for separators
            assert '---' in context
            assert 'Result 1' in context
            assert 'Result 2' in context


class TestCompareCompaniesFix:
    """Test the fix for compare_companies formatting bug."""
    
    def test_compare_companies_returns_string(self):
        """Test that compare_companies returns properly formatted string, not list objects."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            
            # Mock search_by_ticker to return results
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            rag.search_by_ticker = Mock(return_value=[
                {'content': 'Test content', 'metadata': {}}
            ])
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                result = agent._compare_companies("ticker1:AAPL ticker2:MSFT query:revenue")
                
                # Should be a string, not contain list representation
                assert isinstance(result, str)
                assert '[{' not in result  # Should not contain dict/list representation
                assert 'Test content' in result
    
    def test_compare_companies_formats_both_results(self):
        """Test that both companies' data is properly formatted."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            # Mock different results for each ticker
            def mock_search(query, ticker, k):
                if ticker == 'AAPL':
                    return [{'content': 'Apple data', 'metadata': {}}]
                elif ticker == 'MSFT':
                    return [{'content': 'Microsoft data', 'metadata': {}}]
                return []
            
            rag.search_by_ticker = Mock(side_effect=mock_search)
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                result = agent._compare_companies("ticker1:AAPL ticker2:MSFT query:revenue")
                
                # Should contain both companies' data
                assert 'AAPL' in result
                assert 'MSFT' in result
                assert 'Apple data' in result
                assert 'Microsoft data' in result


class TestImprovedErrorMessages:
    """Test improved error messages and feedback."""
    
    def test_query_error_includes_helpful_tip(self):
        """Test that error messages include helpful tips."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 1
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI') as mock_llm:
                # Mock the agent to return a response with no AI content
                mock_agent_executor = Mock()
                mock_agent_executor.invoke.return_value = {
                    'messages': [Mock(type='human', content='test')]
                }
                
                agent = FinancialAnalystAgent(rag)
                agent.agent_executor = mock_agent_executor
                
                result = agent.query("test query")
                
                # Should contain helpful guidance
                assert 'tip' in result.lower() or 'try' in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
