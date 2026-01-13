import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your API key
load_dotenv()
api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env")
    exit()

genai.configure(api_key=api_key)

print("Checking available models for your API key...")
print("-" * 40)

try:
    count = 0
    for m in genai.list_models():
        # Only show models that can generate text (Chat models)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Available: {m.name}")
            count += 1

    if count == 0:
        print("⚠ No chat models found. Check your API key permissions.")

except Exception as e:
    print(f"❌ Error listing models: {e}")