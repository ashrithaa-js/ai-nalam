import json
import google.generativeai as genai
from backend.config import Config
from backend.logger import log_info, log_error

# Configure Gemini
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GOOGLE_API_KEY)

def extract_medical_entities(text: str):
    """
    Extracts medical entities from report text using Gemini and returns structured JSON.
    Specifically targets Test Name, Value, Unit, and Status (low/normal/high).
    """
    try:
        if not Config.GEMINI_API_KEY:
            return []

        # Initialize the model
        model = genai.GenerativeModel(Config.GEMINI_MODEL)

        # Safety-First NER Extraction Prompt
        prompt = f"""
        Extract medical test results from the provided report text and return them as a strictly formatted JSON list.
        
        ### CRITICAL SAFETY RULES:
        1. NO DIAGNOSIS: Do not interpret what the results mean for the user's health condition.
        2. NO HALLUCINATION: Only extract data present in the text. If a value or unit is missing, use "N/A".
        3. ACCURACY: Ensure numerical values match the report exactly.
        4. STATUS LOGIC: Determine status (low/normal/high) ONLY if a clear reference range is provided in the text or context. Otherwise, mark as "Unknown".

        ### JSON SCHEMA:
        Each object must have these exact keys:
        - "test_name": Name of the test
        - "value": The value (or "N/A")
        - "unit": The unit (or "N/A")
        - "status": "low", "normal", "high", or "unknown"

        Report Text:
        {text}
        """

        # Generate response
        response = model.generate_content(prompt)
        
        if response and response.text:
            # Clean response if Gemini included markdown code blocks
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        else:
            return []

    except Exception as e:
        log_error(f"Error during Gemini NER extraction: {str(e)}")
        return []
