"""
Embeddings Module

Generates embeddings using Google AI Studio's embedding models.
"""
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import time
import logging
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import config

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generates embeddings for text chunks using Google AI Studio with rate limiting."""
    
    def __init__(self, model: str = None):
        """
        Initialize the embedding generator.
        
        Args:
            model: Google AI embedding model name
        """
        self.model = model or config.EMBEDDING_MODEL
        
        if not config.GOOGLE_AI_STUDIO_API_KEY:
            logger.warning("GOOGLE_AI_STUDIO_API_KEY not set. Embeddings will fail without it.")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=config.GOOGLE_AI_STUDIO_API_KEY
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        try:
            # Simple retry mechanism for single query
            try:
                return self.embeddings.embed_query(text)
            except Exception:
                logger.warning("Hit rate limit on single query. Sleeping 5s before retry...")
                time.sleep(5)
                return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with Rate Limiting protection.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once (default 10)
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        total_texts = len(texts)
        
        logger.info(f"Starting embedding generation for {total_texts} texts in batches of {batch_size}...")

        try:
            # Loop through the texts in chunks
            for i in range(0, total_texts, batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings for the current batch
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
                
                # Check if we need to pause (don't pause after the last batch)
                if i + batch_size < total_texts:
                    logger.info(f"Processed {i + len(batch)}/{total_texts}. Pausing 2s for rate limits...")
                    time.sleep(2)  # 2 second pause between batches
            
            logger.info(f"Successfully generated embeddings for all {len(all_embeddings)} texts")
            return all_embeddings

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
        print("Make sure GOOGLE_AI_STUDIO_API_KEY is set in .env file")


if __name__ == "__main__":
    main()
