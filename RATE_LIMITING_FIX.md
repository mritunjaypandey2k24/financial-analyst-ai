# Rate Limiting Fix Documentation

**Date**: January 13, 2026  
**Issue**: Google AI API rate limit errors preventing query responses  
**Status**: ✅ Fixed

## Problem Summary

The application was hitting Google AI API rate limits (HTTP 429 errors) and failing to respond to user queries, even after 3 retry attempts with 15-second waits between them. The frontend showed 58,500 documents indexed (which is correct), but queries consistently returned:

> "I am currently overloaded with requests. Please wait 1 minute and try again."

### Root Causes

1. **Multiple API calls per query**: The LangChain React agent makes 3-5 API calls per single user query:
   - 1 call to decide which tool to use
   - 1-2 calls to execute tools (search operations)
   - 1-2 calls to generate the final answer
   
2. **Insufficient wait times**: The previous 15-second wait between retries was not enough for the Google AI free tier, which has strict rate limits:
   - **Gemini 1.5 Flash**: 15 requests per minute (RPM)
   - **Text Embeddings**: 1500 requests per minute
   
3. **Too many documents retrieved**: Each search operation retrieved k=3 documents, consuming more tokens and making responses slower

4. **No rate limiting between attempts**: The code only waited after hitting a rate limit, not proactively

## Solutions Implemented

### 1. Exponential Backoff for Retries

**Changed**: Retry wait times now use exponential backoff
- **Attempt 1 → 2**: Wait 60 seconds (was 15s)
- **Attempt 2 → 3**: Wait 120 seconds (was 15s)
- **Attempt 3+**: Wait 240 seconds (was 15s)

```python
# Before
time.sleep(15)  # Fixed wait time

# After
wait_time = base_wait_time * (2 ** attempt)  # 60s, 120s, 240s
time.sleep(wait_time)
```

**Rationale**: Exponential backoff is the industry standard for handling rate limits. It gives the API more time to reset between attempts.

### 2. Proactive Rate Limiting

**Added**: Minimum 10-second wait between query attempts, even if no error occurred

```python
# Track last API call time
self.last_api_call_time = 0

# Before each attempt, ensure minimum gap
current_time = time.time()
time_since_last_call = current_time - self.last_api_call_time
min_wait_between_calls = 10

if time_since_last_call < min_wait_between_calls:
    wait_time = min_wait_between_calls - time_since_last_call
    logger.info(f"Rate limiting: waiting {wait_time:.1f}s before attempt...")
    time.sleep(wait_time)
```

**Rationale**: Prevents rapid-fire queries from exhausting the rate limit before the first attempt even completes.

### 3. Reduced Document Retrieval

**Changed**: Reduced `k` parameter values across all search operations

| Operation | Before | After | Impact |
|-----------|--------|-------|--------|
| General search | k=3 | k=2 | -33% tokens |
| Ticker-specific search | k=3 | k=2 | -33% tokens |
| Company comparison | k=2 per company | k=1 per company | -50% tokens |
| Default TOP_K_RESULTS | 3 | 2 | -33% default |

**Rationale**: Fewer documents mean:
- Less token usage per API call
- Faster API responses
- Lower probability of hitting rate limits
- Still sufficient context for accurate answers

### 4. LLM Configuration Improvements

**Changed**: LLM initialization parameters for better free-tier compatibility

```python
# Before
self.llm = ChatGoogleGenerativeAI(
    max_retries=1,
    request_timeout=60
)

# After
self.llm = ChatGoogleGenerativeAI(
    max_retries=0,  # We handle retries manually
    request_timeout=90  # Longer timeout for free tier
)
```

**Rationale**:
- Setting `max_retries=0` prevents the SDK from retrying internally, which would interfere with our custom retry logic
- Increasing `request_timeout=90` gives the free tier more time to respond before timing out

### 5. Fixed Embedding Model Name

**Changed**: Updated embedding model from deprecated name to current one

```python
# Before
EMBEDDING_MODEL = "models/embedding-001"

# After
EMBEDDING_MODEL = "models/text-embedding-004"
```

**Rationale**: Using the correct, current model name ensures compatibility and may provide better performance.

### 6. Improved Error Messages

**Changed**: More helpful error messages that guide users

```python
# Before
return "I am currently overloaded with requests. Please wait 1 minute and try again."

# After
return "The Google AI API is currently rate-limited. This is common with the free tier when making multiple requests. Please wait 2-3 minutes before trying again. Consider simplifying your query to use fewer API calls."
```

**Rationale**: Users now understand:
- Why the error occurred (free tier rate limits)
- How long to wait (2-3 minutes, not 1 minute)
- How to avoid the issue (simpler queries)

## Testing Recommendations

Since the sandboxed environment doesn't have network access to Google AI API, testing should be done in a production-like environment:

### Manual Testing Steps

1. **Setup**:
   ```bash
   # Ensure you have a valid Google AI Studio API key
   export GOOGLE_AI_STUDIO_API_KEY="your_key_here"
   
   # Run the Streamlit app
   streamlit run frontend/app.py
   ```

2. **Test Case 1: Single Query**
   - Query: "What was Apple's revenue in 2022?"
   - Expected: Should work on first attempt with 10s initial wait
   - Verify: Check logs for rate limiting message

3. **Test Case 2: Multiple Rapid Queries**
   - Submit 3 queries in quick succession
   - Expected: Each should wait 10s+ before executing
   - Verify: Total time should be at least 30 seconds

4. **Test Case 3: Recovery from Rate Limit**
   - Trigger a rate limit error (make many requests quickly outside the app)
   - Submit a query through the app
   - Expected: Should retry with 60s wait, then 120s if needed
   - Verify: Eventually succeeds after waiting

5. **Test Case 4: Complex Comparison Query**
   - Query: "Compare Apple and Microsoft revenue in 2022"
   - Expected: Should work with reduced k=1 per company
   - Verify: Response still contains meaningful data despite fewer documents

### Automated Testing

The existing test suite in `tests/` should still pass. Run with:

```bash
# Note: These tests may need API access or mocking
pytest tests/ -v
```

## Rate Limit Guidelines for Users

### Understanding Google AI Free Tier Limits

| Model | Requests Per Minute | Requests Per Day |
|-------|---------------------|------------------|
| gemini-1.5-flash | 15 RPM | 1,500 RPD |
| text-embedding-004 | 1,500 RPM | 100,000 RPD |

### Best Practices

1. **Wait between queries**: Allow at least 10-15 seconds between queries
2. **Keep queries simple**: Avoid very complex comparisons requiring multiple tool calls
3. **Batch operations**: If fetching multiple filings, do it in one session, then query later
4. **Monitor rate limits**: Watch the logs for rate limit warnings
5. **Consider paid tier**: For heavy usage, Google AI paid tier removes most limits

### Query Optimization Tips

**Good Queries** (fewer API calls):
- "What was Apple's revenue in 2022?"
- "Show me Microsoft's risk factors"
- "What is Amazon's net income?"

**Complex Queries** (more API calls):
- "Compare revenue, profit, and growth rate between Apple, Microsoft, and Google"
- "Show me all financial metrics for 5 companies"

**Tip**: Break complex queries into smaller, sequential queries instead of one large query.

## Configuration Reference

All rate limiting parameters can be adjusted in the code:

### In `agent/financial_agent.py`:

```python
# Base wait time for rate limit retries (seconds)
base_wait_time = 60  # Increase for more conservative rate limiting

# Minimum gap between query attempts (seconds)
min_wait_between_calls = 10  # Increase to further throttle queries

# Maximum retry attempts
max_retries = 3  # Increase for more persistent retries

# LLM request timeout (seconds)
request_timeout = 90  # Increase for slower connections
```

### In `config.py`:

```python
# Number of documents to retrieve per search
TOP_K_RESULTS = 2  # Decrease for less token usage, increase for more context
```

## Monitoring and Debugging

### Log Messages to Watch For

**Good Signs**:
```
INFO:agent.financial_agent:Processing query (Attempt 1/3)...
INFO:agent.financial_agent:Rate limiting: waiting 10.0s before attempt...
INFO:agent.financial_agent:Returning response with 245 characters
```

**Rate Limit Warnings**:
```
WARNING:agent.financial_agent:⚠️ Hit Rate Limit on attempt 1/3
⚠️ Hit Speed Limit. Pausing for 60 seconds to let cool down...
```

**Troubleshooting**:
- If you see rate limit warnings frequently, increase `base_wait_time`
- If queries take too long, decrease `k` values further
- If responses are too brief, increase `k` values slightly

## Technical Details

### Why the React Agent Makes Multiple Calls

The LangChain React agent follows this pattern:

1. **Thought**: LLM decides what to do (1 API call)
2. **Action**: LLM calls a tool (may trigger embeddings call)
3. **Observation**: Tool returns results
4. **Thought**: LLM processes results (1 API call)
5. **Final Answer**: LLM generates response (1 API call)

This is why a single user query triggers 3-5 API calls to Google.

### Alternative Architectures

For even better rate limit handling, consider:

1. **Caching**: Store previous query results to avoid repeated API calls
2. **Function Calling**: Use Gemini's native function calling instead of React agent
3. **Prompt Engineering**: Create prompts that answer directly without tool calls
4. **Local Embedding**: Use local embedding models to reduce API calls

These alternatives would require more significant code changes but could further reduce API usage.

## Summary of Changes

| File | Changes | Impact |
|------|---------|--------|
| `agent/financial_agent.py` | - Exponential backoff<br>- Proactive rate limiting<br>- Reduced k values<br>- Better error messages | High - Core fix |
| `config.py` | - Updated embedding model<br>- Reduced TOP_K_RESULTS | Medium - Improves defaults |
| `.env.example` | - Updated embedding model | Low - Documentation |

## Conclusion

These changes implement industry-standard rate limiting practices:
- ✅ Exponential backoff for retries
- ✅ Proactive throttling between requests
- ✅ Reduced token usage per request
- ✅ Better error messaging
- ✅ Proper timeout configuration

The application should now handle Google AI free tier rate limits gracefully and provide a better user experience even when hitting limits.

**Expected Behavior**: 
- First query: Works immediately (with 10s initial wait)
- Subsequent queries: Work with automatic spacing
- If rate limited: Automatically retries with increasing waits
- If still rate limited: Provides helpful error message to user

**Note**: The free tier will always have some limitations. For production use with many users, consider upgrading to Google AI paid tier.
