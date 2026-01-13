# Quick Start Guide - Hugging Face Local Models

A condensed guide to get you up and running quickly with the Financial Analyst AI system using local Hugging Face models.

## Prerequisites

- Python 3.8 or higher
- 8GB RAM (16GB recommended)
- 5GB free disk space
- Internet connection (for initial model download only)

## Quick Installation

```bash
# 1. Clone the repository
git clone https://github.com/mritunjaypandey2k24/financial-analyst-ai.git
cd financial-analyst-ai

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set up environment variables
cp .env.example .env
# Edit .env to customize models (defaults work well)
```

## No API Keys Required!

Unlike previous versions, this system runs entirely locally. No external API keys or accounts needed.

## Running the Application

```bash
# Start the Streamlit interface
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`.

**First Run**: Models (~3-4GB) will download automatically. This takes 5-15 minutes. Subsequent runs are instant.

## Quick Usage

1. **Wait for Models** (First Run Only):
   - Models download from Hugging Face Hub
   - Progress shown in terminal
   - One-time process, cached for future use

2. **Fetch Data**:
   - Select companies from the dropdown (e.g., AAPL, MSFT)
   - Choose number of filings (start with 1)
   - Click "Fetch & Index Filings"
   - Wait for indexing (~1-2 minutes per filing)

3. **Ask Questions**:
   - Type your question in the query box
   - Examples:
     - "What was Apple's revenue in 2022?"
     - "Compare AAPL and MSFT revenues"
     - "What are Microsoft's main risk factors?"

4. **View Results**:
   - Read the AI-generated analysis
   - No rate limits - ask as many questions as you want!

## Tips for Best Results

✅ **DO:**
- Include company ticker or name in queries
- Specify time periods (e.g., "fiscal year 2022")
- Mention specific metrics (e.g., "revenue", "net income")
- Start with 1 filing per company to test

❌ **DON'T:**
- Ask vague questions without context
- Query companies you haven't indexed
- Expect instant responses (local models take 10-30 seconds)

## Common First-Time Issues

### Slow Model Download
- Models are large (~3-4GB total)
- Download speed depends on internet connection
- Downloads resume if interrupted
- Only happens once, then cached locally

### Out of Memory Errors
- Enable 8-bit quantization in `.env`:
  ```bash
  USE_8BIT_QUANTIZATION=true
  ```
- Or use smaller models:
  ```bash
  LLM_MODEL=meta-llama/Llama-3.2-1B-Instruct
  ```

### Slow Inference
- Normal on CPU (10-30 seconds per query)
- Much faster with GPU (2-5 seconds)
- Use smaller models for speed
- Consider hardware upgrade for production use

### "No filings found"
- Check that the ticker symbol is correct
- Some companies may not have recent filings
- Try a different company (AAPL, MSFT, GOOGL, AMZN work well)

### "Empty response"
- Ensure filings are indexed successfully
- Make your query more specific
- Include company name and metric

## Quick Examples

### Single Company Query
```
"What was the total revenue of AAPL in fiscal year 2022?"
```

### Comparative Query
```
"Compare AAPL and MSFT revenues in fiscal year 2022"
```

### Trend Analysis
```
"How did Apple's revenue change year-over-year?"
```

### Risk Analysis
```
"What are the main risk factors for Microsoft?"
```

## Performance Optimization

### For Speed
```bash
# In .env file
USE_GPU=true
LLM_MODEL=meta-llama/Llama-3.2-1B-Instruct  # Smaller, faster
```

### For Memory Efficiency
```bash
# In .env file
USE_8BIT_QUANTIZATION=true
BATCH_SIZE=4
```

### For Quality
```bash
# In .env file
LLM_MODEL=HuggingFaceH4/zephyr-7b-beta  # Larger, better
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

## What's Different from Google AI Version?

| Feature | Google AI | Hugging Face Local |
|---------|-----------|-------------------|
| Setup | API key | Model download |
| Cost | Pay per use | Free |
| Speed | Fast | Good (faster with GPU) |
| Privacy | Cloud | Fully local |
| Rate Limits | Yes (strict) | None |
| Offline | No | Yes (after download) |
| Dependencies | External API | Local models |

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [HUGGINGFACE_MIGRATION_GUIDE.md](HUGGINGFACE_MIGRATION_GUIDE.md) for advanced setup
- Explore different models for your use case
- Try different types of queries
- Experiment with multiple companies

## Getting Help

- Review troubleshooting section in README.md
- Check [HUGGINGFACE_MIGRATION_GUIDE.md](HUGGINGFACE_MIGRATION_GUIDE.md)
- Open an issue on GitHub if you encounter problems

---

**Happy analyzing! 📊 Now with full local control and no API limits!**
