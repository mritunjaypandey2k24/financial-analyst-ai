# Manual Testing Guide for Agent Query Fix

## Prerequisites
1. Google AI Studio API key (get from https://makersuite.google.com/app/apikey)
2. Python 3.8+ with all dependencies installed

## Setup

1. **Configure API Key**
   ```bash
   cd /home/runner/work/financial-analyst-ai/financial-analyst-ai
   
   # Create .env file
   cp .env.example .env
   
   # Edit .env and add your API key
   echo "GOOGLE_AI_STUDIO_API_KEY=your_api_key_here" >> .env
   ```

2. **Install Dependencies** (if not already done)
   ```bash
   pip install -r requirements.txt
   ```

## Test Scenario 1: Basic Query (Reproduces Original Issue)

This test reproduces the exact scenario from the problem statement.

1. **Start the Streamlit app**
   ```bash
   streamlit run frontend/app.py
   ```

2. **In the browser:**
   - The app should open at http://localhost:8501
   - In the sidebar, verify API key is configured (green checkmark)
   
3. **Fetch and index filings:**
   - Select ticker: `AAPL`
   - Set number of filings per company: `1`
   - Click "Fetch & Index Filings"
   - Wait for success message (should show number of documents indexed)

4. **Run the query:**
   - In the query box, enter: `What was Apple's revenue in 2022?`
   - Click "Analyze"
   - **Expected Result:** 
     - ✅ The "📊 Analysis Result" section shows a response
     - ✅ Response contains financial information about Apple's revenue
     - ✅ Response is not empty
   - **Before Fix:** Would show empty result
   - **After Fix:** Shows actual revenue information

## Test Scenario 2: Multi-Company Comparison

1. **Fetch filings for multiple companies:**
   - Select tickers: `AAPL`, `MSFT`
   - Set number of filings: `1`
   - Click "Fetch & Index Filings"
   
2. **Run comparison query:**
   - Query: `Compare Apple and Microsoft revenues in 2022`
   - Click "Analyze"
   - **Expected Result:**
     - ✅ Response mentions both companies
     - ✅ Contains specific revenue figures
     - ✅ Provides a comparison

## Test Scenario 3: Information Not Available

1. **Query for unavailable information:**
   - Query: `What was Tesla's revenue in 2025?`
   - Click "Analyze"
   - **Expected Result:**
     - ✅ Response explicitly states information is not available
     - ✅ Response is not empty (provides explanation)

## Test Scenario 4: Empty Query Validation

1. **Try empty query:**
   - Leave query box empty
   - Click "Analyze"
   - **Expected Result:**
     - ✅ Error message: "Please enter a valid query before analyzing"

2. **Try very short query:**
   - Query: `Hi`
   - Click "Analyze"
   - **Expected Result:**
     - ✅ Error message: "Query is too short. Please provide more details."

## Automated Test Run

If you have an API key configured, you can run the automated tests:

```bash
# Set API key in environment
export GOOGLE_AI_STUDIO_API_KEY="your_api_key_here"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent_response.py -v

# Run with detailed output
pytest tests/test_agent_response.py -v -s
```

## Debugging

If you encounter issues, check the console output for debug logs:

```bash
# Run with debug logging
export PYTHONUNBUFFERED=1
streamlit run frontend/app.py
```

Look for log messages like:
- `Processing query (Attempt 1/3)...`
- `Received N messages from agent`
- `Found AI message - content length: X, tool_calls: Y`
- `Returning response with X characters`

## Expected Behavior Summary

### Before Fix
- Agent processes query successfully
- Documents are retrieved from RAG engine
- Agent generates messages but returns empty content
- UI shows empty "📊 Analysis Result" section

### After Fix
- Agent processes query successfully
- Documents are retrieved from RAG engine
- Agent generates complete response with content
- UI displays the actual financial analysis
- If response is still empty, user gets helpful error message

## Troubleshooting

### "No documents available"
- Make sure you clicked "Fetch & Index Filings" first
- Check that the fetch completed successfully
- Verify the ticker symbols are valid

### "429 Resource Exhausted" / Rate Limit Errors
- The agent has built-in retry logic with 15-second delays
- Wait a minute and try again
- Consider using fewer documents or simpler queries

### Empty Response Despite Fix
- Check console logs for errors
- Verify API key is valid
- Ensure documents were actually indexed (check count)
- Try a simpler, more direct query

### Tool Not Calling
- This would show in logs as "No AI message with content found"
- Check that RAG engine has documents
- Verify the query is clear and specific

## Success Criteria

The fix is working correctly if:
1. ✅ Basic queries about revenue return non-empty responses
2. ✅ Responses contain actual financial data
3. ✅ Empty responses show helpful error messages
4. ✅ Multi-company comparisons work
5. ✅ Console logs show proper message processing

## Notes
- First query may take 10-30 seconds due to API calls
- Subsequent queries should be faster
- Rate limits apply (see agent retry logic)
- Test with fresh ChromaDB if needed (delete data/chroma_db)
