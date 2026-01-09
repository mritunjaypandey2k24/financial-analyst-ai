"""
Embeddings Module

Generates embeddings using OpenAI's embedding models.
"""
from typing import List
from langchain_openai import OpenAIEmbeddings
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks using OpenAI."""
    
    def __init__(self, model: str = None):
        """
        Initialize the embedding generator.
        
        Args:
            model: OpenAI embedding model name
        """
        self.model = model or config.EMBEDDING_MODEL
        
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Embeddings will fail without it.")
        
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=config.OPENAI_API_KEY
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise


def main():
    """Example usage of EmbeddingGenerator."""
    generator = EmbeddingGenerator()
    
    sample_texts = [
        "Apple's revenue increased by 8% in 2022",
        "Microsoft reported strong cloud growth",
        "Google's advertising revenue showed resilience"
    ]
    
    try:
        embeddings = generator.generate_embeddings(sample_texts)
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"Failed to generate embeddings: {e}")
        print("Make sure OPENAI_API_KEY is set in .env file")


if __name__ == "__main__":
    main()
