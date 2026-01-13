"""
Tests for content parsing and tool retrieval configuration fixes.

This test suite validates the improvements made to:
1. Handle msg.content as both list and string in the query method
2. Enhanced tool search configuration with k=5
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestContentParsing:
    """Test content parsing in query method."""
    
    def test_content_parsing_with_list(self):
        """Test that query method handles content as a list correctly."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock the agent executor to return a response with list content
                mock_msg = Mock()
                mock_msg.type = 'ai'
                mock_msg.content = [
                    {'text': 'Apple Inc. reported '},
                    {'text': 'revenue of $394.3 billion '},
                    {'text': 'in fiscal year 2022.'}
                ]
                mock_msg.tool_calls = []
                
                mock_response = {
                    'messages': [mock_msg]
                }
                
                with patch.object(agent, 'agent_executor') as mock_executor:
                    mock_executor.invoke.return_value = mock_response
                    
                    result = agent.query("What was Apple's revenue?")
                    
                    # Should concatenate all text parts
                    assert 'Apple Inc. reported' in result
                    assert 'revenue of $394.3 billion' in result
                    assert 'in fiscal year 2022.' in result
                    assert isinstance(result, str)
    
    def test_content_parsing_with_string(self):
        """Test that query method handles content as a string correctly."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock the agent executor to return a response with string content
                mock_msg = Mock()
                mock_msg.type = 'ai'
                mock_msg.content = "Microsoft reported revenue of $198.3 billion in 2022."
                mock_msg.tool_calls = []
                
                mock_response = {
                    'messages': [mock_msg]
                }
                
                with patch.object(agent, 'agent_executor') as mock_executor:
                    mock_executor.invoke.return_value = mock_response
                    
                    result = agent.query("What was Microsoft's revenue?")
                    
                    # Should return the string content directly
                    assert result == "Microsoft reported revenue of $198.3 billion in 2022."
                    assert isinstance(result, str)
    
    def test_content_parsing_with_list_of_objects_with_text_attribute(self):
        """Test parsing when content is a list of objects with text attribute."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock objects with text attribute
                part1 = Mock()
                part1.text = "Google revenue "
                part2 = Mock()
                part2.text = "was $282.8 billion."
                
                mock_msg = Mock()
                mock_msg.type = 'ai'
                mock_msg.content = [part1, part2]
                mock_msg.tool_calls = []
                
                mock_response = {
                    'messages': [mock_msg]
                }
                
                with patch.object(agent, 'agent_executor') as mock_executor:
                    mock_executor.invoke.return_value = mock_response
                    
                    result = agent.query("What was Google's revenue?")
                    
                    # Should concatenate text from objects
                    assert "Google revenue was $282.8 billion." in result
                    assert isinstance(result, str)
    
    def test_content_parsing_with_mixed_list(self):
        """Test parsing when content is a list with mixed types."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock object with text attribute
                part_obj = Mock()
                part_obj.text = " in 2022."
                
                # Mixed list: dict, string, and object
                mock_msg = Mock()
                mock_msg.type = 'ai'
                mock_msg.content = [
                    {'text': 'Revenue was '},
                    '$100 billion',
                    part_obj
                ]
                mock_msg.tool_calls = []
                
                mock_response = {
                    'messages': [mock_msg]
                }
                
                with patch.object(agent, 'agent_executor') as mock_executor:
                    mock_executor.invoke.return_value = mock_response
                    
                    result = agent.query("What was the revenue?")
                    
                    # Should handle all types and concatenate
                    assert "Revenue was" in result
                    assert "$100 billion" in result
                    assert "in 2022." in result
                    assert isinstance(result, str)


class TestToolRetrievalConfiguration:
    """Test enhanced k values in tool methods."""
    
    def test_search_filings_uses_k_5(self):
        """Test that _search_filings uses k=5 for retrieval."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock get_context_for_query to track the k parameter
                with patch.object(rag, 'get_context_for_query', return_value="test context") as mock_context:
                    result = agent._search_filings("test query")
                    
                    # Verify k=5 was used
                    mock_context.assert_called_once_with("test query", k=5)
                    assert result == "test context"
    
    def test_search_by_ticker_uses_k_5(self):
        """Test that _search_by_ticker uses k=5 for retrieval."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                # Mock search_by_ticker to track the k parameter
                mock_results = [{'content': 'Apple revenue data'}]
                with patch.object(rag, 'search_by_ticker', return_value=mock_results) as mock_search:
                    result = agent._search_by_ticker("ticker:AAPL query:revenue")
                    
                    # Verify k=5 was used
                    mock_search.assert_called_once_with("revenue", "AAPL", k=5)
                    assert "Apple revenue data" in result


class TestDebugLogging:
    """Test that debug logging is present."""
    
    def test_debug_print_statement_present(self, capsys):
        """Test that the debug print statement is executed."""
        from agent import FinancialAnalystAgent
        from rag_engine import RAGEngine
        
        with patch('rag_engine.vector_store.RAGEngine._initialize_vector_store') as mock_init, \
             patch('rag_engine.vector_store.GoogleGenerativeAIEmbeddings') as mock_embeddings:
            mock_store = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = 5
            mock_store._collection = mock_collection
            mock_init.return_value = mock_store
            mock_embeddings.return_value = Mock()
            
            rag = RAGEngine()
            
            with patch('agent.financial_agent.ChatGoogleGenerativeAI'):
                agent = FinancialAnalystAgent(rag)
                
                mock_msg = Mock()
                mock_msg.type = 'ai'
                mock_msg.content = "Test response"
                mock_msg.tool_calls = []
                
                mock_response = {
                    'messages': [mock_msg]
                }
                
                with patch.object(agent, 'agent_executor') as mock_executor:
                    mock_executor.invoke.return_value = mock_response
                    
                    result = agent.query("Test query")
                    
                    # Capture stdout to verify debug print
                    captured = capsys.readouterr()
                    assert "🔍 RAW AI RESPONSE:" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
