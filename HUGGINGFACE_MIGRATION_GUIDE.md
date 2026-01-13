# Hugging Face Models Migration Guide

This guide explains the migration from Google AI Studio (Gemini) to Hugging Face models for local inference.

## Overview

The Financial Analyst AI project has been transitioned from using external Google AI Studio APIs to using local Hugging Face models. This provides several benefits:

### Benefits
- **No API Keys Required**: Run everything locally without external dependencies
- **No Rate Limits**: Process as many queries as your hardware allows
- **Privacy**: All data stays on your machine
- **Cost-Effective**: No API usage fees
- **Customization**: Fine-tune models for specific financial analysis tasks
- **Offline Capability**: Works without internet connection (after initial model download)

## What Changed

### 1. Dependencies
- **Removed**: `langchain-google-genai`, `google-generativeai`
- **Added**: `transformers`, `torch`, `sentence-transformers`, `accelerate`, `bitsandbytes`, `langchain-huggingface`

### 2. Configuration (`config.py`)
- Replaced Google AI API key configuration
- Added model cache directory for storing downloaded models
- Added Hugging Face model names for embeddings and LLM
- Added GPU/CPU configuration and quantization settings

### 3. Embeddings (`rag_engine/embeddings.py`)
- Replaced `GoogleGenerativeAIEmbeddings` with `SentenceTransformer`
- Removed API rate limiting (not needed for local models)
- Added support for GPU acceleration
- Faster batch processing with no delays between batches

### 4. Vector Store (`rag_engine/vector_store.py`)
- Updated to use `HuggingFaceEmbeddings` from `langchain-huggingface`
- Removed rate limiting delays
- Increased batch size from 10 to 50 for faster processing

### 5. AI Agent (`agent/financial_agent.py`)
- Created new `LocalLLM` class for Hugging Face model integration
- Removed Google AI Studio LLM initialization
- Removed rate limiting logic
- Simplified error handling (no retry logic for API limits)

### 6. New Local LLM Module (`agent/local_llm.py`)
- Wrapper for Hugging Face language models
- Supports 8-bit quantization for memory efficiency
- GPU acceleration when available
- Compatible with LangChain's agent framework

## Model Selection

### Embedding Models
The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`:
- **Size**: ~80MB
- **Embedding Dimension**: 384
- **Speed**: Very fast
- **Quality**: Good for most tasks

Alternative options:
```python
# Higher quality, slower (420MB)
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Good balance (130MB)
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Financial-specific (if available)
EMBEDDING_MODEL=sentence-transformers/multi-qa-mpnet-base-dot-v1
```

### LLM Models
The default LLM is `meta-llama/Llama-3.2-3B-Instruct`:
- **Size**: ~3GB (or ~1.5GB with 8-bit quantization)
- **Parameters**: 3 billion
- **Context Length**: 4096 tokens
- **Performance**: Good balance between speed and quality

Alternative options:
```python
# Smaller, faster (1B params, ~1GB)
LLM_MODEL=meta-llama/Llama-3.2-1B-Instruct

# Compact chat model (3.8B params, ~4GB)
LLM_MODEL=microsoft/Phi-3-mini-4k-instruct

# Higher quality (7B params, ~7GB)
LLM_MODEL=HuggingFaceH4/zephyr-7b-beta

# Smallest option (0.5B params, ~500MB)
LLM_MODEL=microsoft/phi-2
```

## Hardware Requirements

### Minimum Requirements (CPU Only)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB for models and dependencies
- **CPU**: Modern multi-core processor
- **Performance**: Slower inference, but functional

### Recommended (with GPU)
- **GPU**: NVIDIA GPU with 6GB+ VRAM
- **RAM**: 16GB system RAM
- **Storage**: 10GB for models and cache
- **Performance**: 5-10x faster inference

## Setup Instructions

### 1. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install torch transformers sentence-transformers accelerate langchain-huggingface
```

### 2. Configure Models

Edit `.env` file or set environment variables:

```bash
# Model selection
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct

# Performance settings
USE_8BIT_QUANTIZATION=true  # Reduces memory usage by ~50%
USE_GPU=true                # Use GPU if available
MAX_NEW_TOKENS=512          # Maximum response length
TEMPERATURE=0.1             # Lower = more focused responses

# Directories
MODEL_CACHE_DIR=./data/model_cache
```

### 3. Download Models (First Run)

On first run, models will be downloaded automatically from Hugging Face:

```bash
# Test embedding model download
python3 -c "from rag_engine.embeddings import EmbeddingGenerator; EmbeddingGenerator()"

# Test LLM download (this may take a while)
python3 -c "from agent.local_llm import LocalLLM; LocalLLM()"
```

**Note**: Initial download requires internet connection. Models are cached locally in `MODEL_CACHE_DIR` for offline use.

### 4. Run the Application

```bash
# Start the Streamlit interface
streamlit run frontend/app.py

# Or use programmatically
python3 demo.py
```

## Performance Optimization

### 1. Enable 8-bit Quantization
Reduces memory usage with minimal quality impact:
```bash
USE_8BIT_QUANTIZATION=true
```

### 2. Adjust Batch Sizes
For limited RAM, reduce batch sizes in `config.py`:
```python
BATCH_SIZE = 4  # Default is 8
```

### 3. Choose Smaller Models
For resource-constrained systems:
```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 80MB
LLM_MODEL=meta-llama/Llama-3.2-1B-Instruct  # 1GB
```

### 4. GPU Acceleration
Dramatically improves performance:
```bash
# Install CUDA version of PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Enable GPU
USE_GPU=true
```

## Troubleshooting

### Out of Memory Errors
1. Enable 8-bit quantization: `USE_8BIT_QUANTIZATION=true`
2. Use smaller models (see model selection above)
3. Reduce batch size: `BATCH_SIZE=4`
4. Close other applications to free RAM

### Slow Inference
1. Enable GPU if available: `USE_GPU=true`
2. Use smaller models for faster responses
3. Reduce `MAX_NEW_TOKENS` to limit response length
4. Increase `BATCH_SIZE` if you have sufficient RAM

### Model Download Fails
1. Check internet connection
2. Try again (downloads resume automatically)
3. Manually download models from Hugging Face and place in `MODEL_CACHE_DIR`
4. Check firewall/proxy settings

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check PyTorch installation
python3 -c "import torch; print(torch.__version__)"

# Check transformers installation
python3 -c "import transformers; print(transformers.__version__)"
```

## Fine-tuning for Financial Domain

For advanced users, models can be fine-tuned on financial data:

### 1. Prepare Financial Dataset
```python
# Create training data from 10-K filings
from data_ingestion import SECFilingFetcher

fetcher = SECFilingFetcher()
filings = fetcher.fetch_multiple_tickers(['AAPL', 'MSFT', 'GOOGL'])
# Process filings into Q&A pairs for training
```

### 2. Fine-tune Embedding Model
```bash
# Using sentence-transformers training script
python3 train_embeddings.py --base-model sentence-transformers/all-MiniLM-L6-v2 \
    --training-data financial_qa_pairs.json \
    --output-dir ./models/financial-embeddings
```

### 3. Fine-tune LLM
```bash
# Using Hugging Face transformers
python3 fine_tune_llm.py --base-model meta-llama/Llama-3.2-3B-Instruct \
    --training-data financial_instructions.json \
    --output-dir ./models/financial-llm
```

### 4. Use Fine-tuned Models
```bash
EMBEDDING_MODEL=./models/financial-embeddings
LLM_MODEL=./models/financial-llm
```

## Comparison with Google AI Studio

| Aspect | Google AI Studio | Hugging Face Local |
|--------|------------------|-------------------|
| Setup Complexity | Simple (API key) | Moderate (model download) |
| Cost | Pay per use | Free (after setup) |
| Speed | Fast (cloud GPUs) | Varies (hardware dependent) |
| Privacy | Data sent to Google | Fully local |
| Rate Limits | Yes (strict on free tier) | None |
| Customization | Limited | Full control |
| Offline Usage | No | Yes (after download) |
| Model Updates | Automatic | Manual |

## Migration Checklist

- [x] Update `requirements.txt` with Hugging Face dependencies
- [x] Modify `config.py` to use local models
- [x] Replace embedding generation in `embeddings.py`
- [x] Update vector store in `vector_store.py`
- [x] Create `local_llm.py` for LLM inference
- [x] Update `financial_agent.py` to use local LLM
- [x] Remove Google API key from `.env.example`
- [x] Update documentation
- [x] Test with sample queries

## Support

For issues or questions:
1. Check this migration guide
2. Review the README.md
3. Check Hugging Face model documentation
4. Open a GitHub issue

## Resources

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [LangChain Hugging Face Integration](https://python.langchain.com/docs/integrations/llms/huggingface_pipelines)
- [Model Quantization Guide](https://huggingface.co/docs/transformers/main_classes/quantization)
