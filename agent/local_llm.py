"""
Local LLM Module

Wrapper for Hugging Face language models to work with LangChain.
Provides local inference without external API dependencies.
"""
import logging
import torch
from typing import Any, List, Optional
from langchain_huggingface import HuggingFacePipeline
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    pipeline,
    BitsAndBytesConfig
)
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local Large Language Model wrapper using Hugging Face transformers.
    Supports quantization and GPU acceleration for efficient inference.
    """
    
    def __init__(self, model_name: str = None, use_8bit: bool = None):
        """
        Initialize the local LLM.
        
        Args:
            model_name: Hugging Face model name/path
            use_8bit: Whether to use 8-bit quantization (default from config)
        """
        self.model_name = model_name or config.LLM_MODEL
        self.use_8bit = use_8bit if use_8bit is not None else config.USE_8BIT_QUANTIZATION
        
        # Determine device
        if config.USE_GPU and torch.cuda.is_available():
            self.device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = "cpu"
            logger.info("Using CPU")
        
        # Load model and tokenizer
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer."""
        logger.info(f"Loading model: {self.model_name}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=str(config.MODEL_CACHE_DIR),
                trust_remote_code=True
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization if using 8-bit
            quantization_config = None
            if self.use_8bit and self.device == "cuda":
                logger.info("Using 8-bit quantization")
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0
                )
            
            # Load model
            model_kwargs = {
                "cache_dir": str(config.MODEL_CACHE_DIR),
                "trust_remote_code": True,
                "low_cpu_mem_usage": True
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            elif self.device == "cuda":
                model_kwargs["device_map"] = "auto"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=config.MAX_NEW_TOKENS,
                temperature=config.TEMPERATURE,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_langchain_llm(self) -> HuggingFacePipeline:
        """
        Get a LangChain-compatible LLM wrapper.
        
        Returns:
            HuggingFacePipeline instance
        """
        return HuggingFacePipeline(pipeline=self.pipeline)
    
    def generate(self, prompt: str, max_new_tokens: int = None) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate (overrides config)
            
        Returns:
            Generated text
        """
        try:
            # Use provided max_new_tokens or default from config
            tokens = max_new_tokens if max_new_tokens is not None else config.MAX_NEW_TOKENS
            
            # Generate with explicit parameters (thread-safe)
            result = self.pipeline(
                prompt,
                max_new_tokens=tokens,
                return_full_text=False  # Only return generated text
            )
            
            # Extract generated text
            generated_text = result[0]['generated_text']
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise


def main():
    """Example usage of LocalLLM."""
    try:
        llm = LocalLLM()
        
        prompt = "What is financial analysis?"
        print(f"Prompt: {prompt}")
        print("Generating response...")
        
        response = llm.generate(prompt)
        print(f"\nResponse: {response}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
