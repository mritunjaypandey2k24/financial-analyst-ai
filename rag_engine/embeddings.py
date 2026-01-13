"""
Embeddings Module

Generates embeddings using Hugging Face sentence-transformers models locally.
"""
from typing import List
import logging
import torch
from sentence_transformers import SentenceTransformer
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks using Hugging Face models locally."""
    
    def __init__(self, model: str = None):
        """
        Initialize the embedding generator.
        
        Args:
            model: Hugging Face model name for embeddings
        """
        self.model_name = model or config.EMBEDDING_MODEL
        
        # Determine device (GPU if available and enabled, otherwise CPU)
        if config.USE_GPU and torch.cuda.is_available():
            self.device = "cuda"
            logger.info(f"Using GPU for embeddings: {torch.cuda.get_device_name(0)}")
        else:
            self.device = "cpu"
            logger.info("Using CPU for embeddings")
        
        # Load the sentence-transformer model
        logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(config.MODEL_CACHE_DIR),
                device=self.device
            )
            logger.info(f"Successfully loaded embedding model on {self.device}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once (default from config)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        batch_size = batch_size or config.BATCH_SIZE
        total_texts = len(texts)
        
        logger.info(f"Generating embeddings for {total_texts} texts in batches of {batch_size}...")
        
        try:
            # Process all texts at once with batch processing handled internally
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_tensor=False,
                show_progress_bar=True,
                normalize_embeddings=True
            )
            
            logger.info(f"Successfully generated embeddings for all {len(embeddings)} texts")
            return embeddings.tolist()
            
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


if __name__ == "__main__":
    main()
