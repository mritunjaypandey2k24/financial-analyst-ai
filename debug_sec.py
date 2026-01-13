import os
from sec_edgar_downloader import Downloader
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

def test_sec_connection():
    user_agent = os.getenv("USER_AGENT")
    print(f"1. Checking User-Agent: {user_agent}")
    
    if not user_agent or "example.com" in user_agent:
        print("❌ Error: Invalid User-Agent found. Please update .env")
        return

    print("2. Attempting to download 1 Apple (AAPL) 10-K...")
    
    try:
        # Initialize with the exact string from .env
        company_name, email = user_agent.split('<')
        email = email.strip('>')
        dl = Downloader(company_name.strip(), email)
        
        # Try download
        num_downloaded = dl.get("10-K", "AAPL", limit=1)
        
        if num_downloaded > 0:
            print(f"✅ Success! Downloaded {num_downloaded} filing.")
            print(f"   Files are located in: {os.getcwd()}/sec-edgar-filings")
        else:
            print("⚠ Connection successful, but 0 files returned.")
            print("   (This usually means the SEC is rate-limiting your IP temporarily)")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        print("   If the error says '403 Client Error', the User-Agent is still being rejected.")

if __name__ == "__main__":
    test_sec_connection()