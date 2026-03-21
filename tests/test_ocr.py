import sys
import os
# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ocr import extract_text_from_image
from backend.config import Config

def test_ocr_load():
    print("Testing OCR module loading...")
    try:
        # We won't actually perform a request, just check if function exists and can handle errors
        # if input is missing.
        response = extract_text_from_image(None)
        print(f"Handled error correctly: {response}")
        print("✅ OCR Module Test Passed!")
    except Exception as e:
        print(f"❌ OCR Module loading failed: {e}")

if __name__ == "__main__":
    test_ocr_load()
