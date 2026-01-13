"""
Financial Analyst AI - Streamlit Frontend

A user-friendly interface for querying and analyzing SEC 10-K filings
using AI-powered financial analysis.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_ingestion import SECFilingFetcher
from rag_engine import RAGEngine
from agent import FinancialAnalystAgent
import config


# Page configuration
st.set_page_config(
    page_title="Financial Analyst AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the RAG engine and agent (cached)."""
    try:
        rag = RAGEngine()
        agent = FinancialAnalystAgent(rag)
        return rag, agent
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return None, None


def fetch_and_index_filings(tickers, num_filings=1):
    """Fetch SEC filings and add them to the RAG engine."""
    rag, _ = initialize_system()
    
    if not rag:
        return False
    
    fetcher = SECFilingFetcher()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_documents = []
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Fetching {ticker} filings...")
        
        try:
            filings = fetcher.fetch_10k_filing(ticker, num_filings)
            
            if filings:
                all_documents.extend(filings)
                st.success(f"✓ Fetched {len(filings)} filing(s) for {ticker}")
            else:
                st.warning(f"⚠ No filings found for {ticker}")
        
        except Exception as e:
            st.error(f"✗ Error fetching {ticker}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(tickers))
    
    # Index documents
    if all_documents:
        status_text.text("Indexing documents...")
        try:
            rag.add_documents(all_documents)
            st.success(f"✓ Successfully indexed {len(all_documents)} filing(s)")
            return True
        except Exception as e:
            st.error(f"✗ Error indexing documents: {str(e)}")
            return False
    
    return False


def create_sample_visualization(data_dict):
    """Create a sample bar chart for comparative data."""
    if not data_dict:
        return None
    
    df = pd.DataFrame(list(data_dict.items()), columns=['Company', 'Value'])
    
    fig = px.bar(
        df,
        x='Company',
        y='Value',
        title='Comparative Analysis',
        labels={'Value': 'Amount ($B)', 'Company': 'Company'},
        color='Company',
        text='Value'
    )
    
    fig.update_traces(texttemplate='%{text:.2f}B', textposition='outside')
    fig.update_layout(showlegend=False)
    
    return fig


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<p class="main-header">📊 Financial Analyst AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered SEC 10-K Filing Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # API Key check
    if not config.GOOGLE_AI_STUDIO_API_KEY or config.GOOGLE_AI_STUDIO_API_KEY == "":
        st.sidebar.error("⚠️ Google AI Studio API Key not configured!")
        st.sidebar.info("Please set GOOGLE_AI_STUDIO_API_KEY in your .env file")
        api_key = st.sidebar.text_input("Or enter API key here:", type="password")
        if api_key:
            config.GOOGLE_AI_STUDIO_API_KEY = api_key
    else:
        st.sidebar.success("✓ Google AI Studio API Key configured")
    
    # Ticker selection
    st.sidebar.subheader("📈 Select Companies")
    default_tickers = config.DEFAULT_TICKERS
    
    available_tickers = st.sidebar.multiselect(
        "Choose tickers to analyze:",
        options=["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM"],
        default=["AAPL", "MSFT"]
    )
    
    custom_ticker = st.sidebar.text_input("Or add custom ticker:")
    if custom_ticker:
        available_tickers.append(custom_ticker.upper())
    
    num_filings = st.sidebar.slider("Number of filings per company:", 1, 3, 1)
    
    # Fetch data button
    if st.sidebar.button("🔄 Fetch & Index Filings", type="primary"):
        if not available_tickers:
            st.sidebar.warning("Please select at least one ticker")
        else:
            with st.spinner("Fetching and indexing filings..."):
                success = fetch_and_index_filings(available_tickers, num_filings)
                if success:
                    st.balloons()
    
    st.sidebar.divider()
    
    # Example queries
    st.sidebar.subheader("💡 Example Queries")
    example_queries = [
        "What was Apple's revenue in 2022?",
        "Compare AAPL and MSFT revenues",
        "What are the main risk factors for Microsoft?",
        "Compare profit margins between companies",
        "What was the year-over-year growth?"
    ]
    
    for example in example_queries:
        if st.sidebar.button(example, key=example):
            st.session_state['current_query'] = example
    
    # Main content area
    tabs = st.tabs(["🔍 Query Analysis", "📚 About"])
    
    with tabs[0]:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **How to use:**
        1. Configure your Google AI Studio API key in the sidebar
        2. Select companies to analyze
        3. Click "Fetch & Index Filings" to download and process SEC 10-K filings
        4. Ask questions about the companies' financial data
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Initialize system
        rag, agent = initialize_system()
        
        if not rag or not agent:
            st.error("System initialization failed. Please check your configuration.")
            st.stop()
        
        # Display document count status
        try:
            doc_count = rag.get_document_count()
            if doc_count > 0:
                st.success(f"📚 {doc_count} documents indexed and ready for analysis")
            else:
                st.warning("⚠️ No documents indexed yet. Please fetch and index filings first.")
        except Exception as e:
            st.info("📊 Document status: Unable to retrieve count")
        
        # Query input
        st.subheader("🤔 Ask a Question")
        
        # Use session state for query
        if 'current_query' not in st.session_state:
            st.session_state['current_query'] = ""
        
        query = st.text_area(
            "Enter your financial analysis query:",
            value=st.session_state['current_query'],
            height=100,
            placeholder="e.g., Compare the revenue of Apple and Microsoft in 2022"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            analyze_button = st.button("🚀 Analyze", type="primary")
        with col2:
            if st.button("🗑️ Clear"):
                st.session_state['current_query'] = ""
                st.rerun()
        
        # Validate and process query
        if analyze_button:
            # Validate query input
            if not query or not query.strip():
                st.error("❌ Please enter a valid query before analyzing.")
            elif len(query.strip()) < 5:
                st.error("❌ Query is too short. Please provide more details.")
            elif len(query) > 1000:
                st.error("❌ Query is too long. Please keep it under 1000 characters.")
            else:
                # Check if documents are available
                if not rag.has_documents():
                    st.error("❌ No documents available. Please fetch and index SEC 10-K filings first using the sidebar.")
                else:
                    with st.spinner("🤖 Analyzing your query..."):
                        try:
                            # Get response from agent
                            response = agent.query(query.strip())
                            
                            # Display response
                            st.subheader("📊 Analysis Result")
                            st.markdown(response)
                            
                            # Try to extract numerical data for visualization
                            # This is a simple example - you could enhance this with more sophisticated parsing
                            st.divider()
                            st.subheader("📈 Visualization")
                            
                            # Example: Create a simple visualization placeholder
                            st.info("💡 Tip: For numeric comparisons, visualizations will be generated automatically.")
                            
                            # You could add logic here to parse response and create charts
                            # For demonstration, show a sample chart structure
                            if "compare" in query.lower() or "versus" in query.lower():
                                st.caption("Chart would appear here based on extracted data")
                        
                        except Exception as e:
                            st.error(f"❌ Error processing query: {str(e)}")
                            st.info("💡 Tip: Try rephrasing your query or check if the relevant companies' filings are indexed.")
        
        # Search results section
        if query and not analyze_button:
            st.info("👆 Click 'Analyze' to get AI-powered insights on your query")
    
    with tabs[1]:
        st.header("About Financial Analyst AI")
        
        st.markdown("""
        ### 🎯 Purpose
        This application leverages AI to analyze SEC 10-K filings, providing intelligent 
        insights into company financial performance and enabling comparative analysis.
        
        ### 🛠️ Technology Stack
        - **LangChain**: Framework for building LLM applications
        - **Google AI Studio (Gemini)**: AI models for analysis and embeddings
        - **ChromaDB**: Vector database for efficient document retrieval
        - **Streamlit**: Interactive web interface
        - **SEC EDGAR**: Source of financial filings
        
        ### 📊 Features
        - Fetch and parse SEC 10-K filings automatically
        - Intelligent question-answering using RAG (Retrieval-Augmented Generation)
        - Comparative analysis between companies
        - Natural language queries
        - Visual representations of financial data
        
        ### 🔒 Privacy
        - Your API key is stored locally and never transmitted except to Google AI Studio
        - SEC filings are publicly available data
        - All processing happens on your machine or authorized cloud services
        
        ### 📝 Notes
        - This tool is for research and educational purposes
        - Always verify important financial information from official sources
        - SEC 10-K filings are historical data and may not reflect current conditions
        """)
        
        st.divider()
        
        st.subheader("🏗️ System Architecture")
        st.markdown("""
        1. **Data Ingestion**: Fetches 10-K filings from SEC EDGAR
        2. **RAG Engine**: Processes documents, creates embeddings, stores in ChromaDB
        3. **AI Agent**: Uses Google AI Studio LLM with access to RAG tools for intelligent analysis
        4. **Frontend**: Streamlit interface for user interaction
        """)


if __name__ == "__main__":
    main()
