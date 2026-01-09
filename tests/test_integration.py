"""
Integration tests for the complete Financial Analyst AI pipeline.
"""
import pytest
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.skipif(
    not os.getenv("GOOGLE_AI_STUDIO_API_KEY"),
    reason="Google AI Studio API key required for integration tests"
)
class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_flow(self, tmp_path):
        """Test the complete flow from data ingestion to query."""
        from data_ingestion.fetch_10k import SECFilingFetcher
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        
        # Create sample documents (instead of fetching real ones for testing)
        sample_docs = [
            {
                'content': 'Apple Inc. reported total net sales of $394.3 billion for fiscal year 2022.',
                'ticker': 'AAPL',
                'filing_date': '2022-10-28',
                'file_path': str(tmp_path / 'aapl.txt')
            }
        ]
        
        # Initialize RAG engine with test directory
        import config
        config.CHROMA_DB_DIR = tmp_path / "chroma_test"
        
        rag = RAGEngine(collection_name="test_collection")
        
        # Add documents
        rag.add_documents(sample_docs)
        
        # Search
        results = rag.search("What was Apple's revenue?", k=1)
        
        assert len(results) > 0
        assert 'AAPL' in results[0]['metadata']['ticker']
    
    def test_rag_and_agent_integration(self, tmp_path):
        """Test RAG engine with agent."""
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        
        # Setup
        import config
        config.CHROMA_DB_DIR = tmp_path / "chroma_test_agent"
        
        rag = RAGEngine(collection_name="test_agent_collection")
        
        # Add sample data
        sample_docs = [
            {
                'content': 'Microsoft Corporation reported revenue of $198.3 billion in fiscal year 2022.',
                'ticker': 'MSFT',
                'filing_date': '2022-07-30',
                'file_path': str(tmp_path / 'msft.txt')
            }
        ]
        
        rag.add_documents(sample_docs)
        
        # Create agent
        agent = FinancialAnalystAgent(rag)
        
        # Query
        response = agent.query("What was Microsoft's revenue in 2022?")
        
        assert response is not None
        assert len(response) > 0


class TestConfigurationValidation:
    """Test configuration and setup."""
    
    def test_config_import(self):
        """Test that config module can be imported."""
        import config
        
        assert hasattr(config, 'DATA_DIR')
        assert hasattr(config, 'CHROMA_DB_DIR')
        assert hasattr(config, 'CHUNK_SIZE')
    
    def test_module_imports(self):
        """Test that all main modules can be imported."""
        from data_ingestion import SECFilingFetcher
        from rag_engine import RAGEngine
        from agent import FinancialAnalystAgent
        
        assert SECFilingFetcher is not None
        assert RAGEngine is not None
        assert FinancialAnalystAgent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
