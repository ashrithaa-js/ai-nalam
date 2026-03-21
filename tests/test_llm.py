import sys
import os
# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm import generate_response
from backend.config import Config

def test_gemini_connection():
    print(f"Testing Gemini Model: {Config.GEMINI_MODEL}")
    prompt = "Hello, are you functional? Respond with 'Yes' only."
    try:
        response = generate_response(prompt)
        print(f"Response: {response}")
        if "Yes" in response:
            print("✅ Gemini Connection Test Passed!")
        else:
            print("⚠️ Gemini responded, but unexpected content.")
    except Exception as e:
        print(f"❌ Gemini Connection Test Failed: {e}")

if __name__ == "__main__":
    test_gemini_connection()
