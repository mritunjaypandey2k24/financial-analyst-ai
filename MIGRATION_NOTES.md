# Migration from OpenAI to Google AI Studio API

## Overview

This document describes the migration from OpenAI API to Google AI Studio (Gemini) API for the Financial Analyst AI project. All references to OpenAI have been replaced with Google AI Studio equivalents.

## Changes Made

### 1. Configuration Files

#### `config.py`
- **Changed**: `OPENAI_API_KEY` → `GOOGLE_AI_STUDIO_API_KEY`
- **Changed**: `EMBEDDING_MODEL` default from `text-embedding-ada-002` → `models/embedding-001`
- **Changed**: `LLM_MODEL` default from `gpt-3.5-turbo` → `gemini-1.5-flash`

#### `.env.example`
- Updated environment variable template to use `GOOGLE_AI_STUDIO_API_KEY`
- Updated model configuration defaults

### 2. Dependencies

#### `requirements.txt`
**Removed:**
- `openai`
- `langchain-openai`

**Added:**
- `google-generativeai`
- `langchain-google-genai`

**Retained:**
- `langchain`
- `langchain-community`
- `langchain-core`
- `langchain-text-splitters`
- `langgraph`
- All other dependencies remain unchanged

### 3. Code Changes

#### `agent/financial_agent.py`
- **Import Changed**: `from langchain_openai import ChatOpenAI` → `from langchain_google_genai import ChatGoogleGenerativeAI`
- **Class Changed**: `ChatOpenAI` → `ChatGoogleGenerativeAI`
- **Parameter Changed**: `openai_api_key` → `google_api_key`
- **Config Reference**: `config.OPENAI_API_KEY` → `config.GOOGLE_AI_STUDIO_API_KEY`

#### `rag_engine/embeddings.py`
- **Import Changed**: `from langchain_openai import OpenAIEmbeddings` → `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- **Class Changed**: `OpenAIEmbeddings` → `GoogleGenerativeAIEmbeddings`
- **Parameter Changed**: `openai_api_key` → `google_api_key`
- **Config Reference**: `config.OPENAI_API_KEY` → `config.GOOGLE_AI_STUDIO_API_KEY`

#### `rag_engine/vector_store.py`
- **Import Changed**: `from langchain_openai import OpenAIEmbeddings` → `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- **Class Changed**: `OpenAIEmbeddings` → `GoogleGenerativeAIEmbeddings`
- **Parameter Changed**: `openai_api_key` → `google_api_key`
- **Config Reference**: `config.OPENAI_API_KEY` → `config.GOOGLE_AI_STUDIO_API_KEY`

#### `frontend/app.py`
- Updated API key configuration check to use `config.GOOGLE_AI_STUDIO_API_KEY`
- Updated user messages to reference "Google AI Studio" instead of "OpenAI"
- Updated documentation strings within the app

#### `demo.py`
- Updated demo text to reference "Google AI embedding generation" instead of "OpenAI"
- Updated instructions to reference `GOOGLE_AI_STUDIO_API_KEY`

#### `validate.py`
- Updated feature descriptions to reference "Google AI" instead of "OpenAI"
- Updated instructions to reference `GOOGLE_AI_STUDIO_API_KEY`

### 4. Documentation Updates

#### `README.md`
- Updated overview to reference Google AI Studio's Gemini models
- Updated prerequisites to require Google AI Studio API key
- Updated configuration section with new environment variables
- Updated all troubleshooting sections
- Updated technology stack acknowledgments
- Updated security and privacy sections

#### `docs/API.md`
- Updated `EmbeddingGenerator` documentation
- Updated environment variables section
- Updated configuration examples
- Updated error handling documentation

#### `docs/GETTING_STARTED.md`
- Updated setup instructions for Google AI Studio API key
- Updated configuration steps
- Updated troubleshooting section
- Updated best practices

#### `docs/PROJECT_COMPLETION.md`
- Updated technology stack section
- Updated feature descriptions
- Updated API integration references

#### `docs/SECURITY.md`
- Updated dependency table to replace `langchain-openai` with `langchain-google-genai`
- Updated expected package versions

### 5. Security & Privacy

#### `.gitignore`
- **Verified**: `.env` file is already excluded (line 140)
- No sensitive API keys are hardcoded in the repository
- All API key references use environment variables

## Migration Checklist for Users

If you're upgrading an existing installation:

1. **Get a Google AI Studio API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create or select a project
   - Generate an API key

2. **Update Environment Variables**
   ```bash
   # Old .env
   OPENAI_API_KEY=your_openai_key
   
   # New .env
   GOOGLE_AI_STUDIO_API_KEY=your_google_ai_studio_key
   ```

3. **Update Model Configuration (Optional)**
   ```bash
   # Default models (already set if you don't specify):
   EMBEDDING_MODEL=models/embedding-001
   LLM_MODEL=gemini-1.5-flash
   
   # Other available Gemini models:
   # LLM_MODEL=gemini-1.5-pro
   # LLM_MODEL=gemini-pro
   ```

4. **Reinstall Dependencies**
   ```bash
   pip uninstall openai langchain-openai
   pip install -r requirements.txt
   ```

5. **Clear Old Vector Store (Recommended)**
   ```bash
   rm -rf data/chroma_db
   ```
   
   This ensures embeddings are regenerated with the new Google AI model.

6. **Re-index Documents**
   - Fetch and index your SEC filings again
   - This will use the new Google AI embeddings

## API Differences

### Embedding Models
- **OpenAI**: `text-embedding-ada-002` (1536 dimensions)
- **Google AI**: `models/embedding-001` (768 dimensions)

### Language Models
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, etc.
- **Google AI**: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`

### API Authentication
- **OpenAI**: Uses `Authorization: Bearer <token>` header
- **Google AI**: Uses API key in request parameters or headers

### Rate Limits
- Both services have rate limits
- Google AI Studio has generous free tier quotas
- Check [Google AI Studio pricing](https://ai.google.dev/pricing) for current limits

## Benefits of Google AI Studio

1. **Cost-Effective**: Generous free tier for development and testing
2. **Performance**: Gemini models offer competitive performance
3. **Integration**: Native Google Cloud integration options
4. **Multi-modal**: Support for text, images, and more (future expansion)
5. **Long Context**: Gemini 1.5 models support very long context windows

## Troubleshooting

### "GOOGLE_AI_STUDIO_API_KEY not set"
- Ensure your `.env` file exists and contains the key
- Check the key is not wrapped in quotes in the `.env` file
- Verify the key is valid by testing in [AI Studio](https://aistudio.google.com/)

### "Error generating embeddings"
- Verify your API key is active
- Check you haven't exceeded rate limits
- Ensure your Google Cloud project has the Generative AI API enabled

### "Model not found" errors
- Use valid Gemini model names:
  - `gemini-1.5-flash` (fastest, recommended for most use cases)
  - `gemini-1.5-pro` (more capable, higher cost)
  - `gemini-pro` (stable, older version)

### Different Search Results
- Embeddings from different models may produce slightly different results
- Re-indexing documents with the new embedding model is recommended
- Adjust `TOP_K_RESULTS` in config if needed

## Testing

After migration, test the following:

1. **Basic Import Test**
   ```bash
   python validate.py
   ```

2. **Embedding Generation**
   ```bash
   python -c "from rag_engine.embeddings import EmbeddingGenerator; gen = EmbeddingGenerator(); print('Success!')"
   ```

3. **Full Pipeline Test**
   ```bash
   streamlit run frontend/app.py
   ```

4. **Run Tests** (with API key set)
   ```bash
   pytest tests/ -v
   ```

## Rollback Instructions

If you need to rollback to OpenAI:

1. Checkout the previous commit before this migration
2. Restore your `.env` file with `OPENAI_API_KEY`
3. Reinstall dependencies from the old `requirements.txt`
4. Clear and re-index your vector store

## Additional Resources

- [Google AI Studio Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api/python/google/generativeai)
- [LangChain Google GenAI Integration](https://python.langchain.com/docs/integrations/providers/google_generative_ai)
- [Getting Started with Google AI](https://ai.google.dev/tutorials/python_quickstart)

## Support

For issues related to:
- **This migration**: Open an issue on the GitHub repository
- **Google AI Studio**: Visit [Google AI Developer Forum](https://developers.googleblog.com/google-ai/)
- **LangChain integration**: Check [LangChain Documentation](https://python.langchain.com/docs/)

---

**Migration Date**: January 2026  
**Migration Version**: From OpenAI API to Google AI Studio API  
**Status**: ✅ Complete and Tested
