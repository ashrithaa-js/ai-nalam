import google.generativeai as genai
from PIL import Image
from backend.config import Config
from backend.logger import log_info, log_error

def extract_text_from_image(image_file) -> str:
    try:
        if not Config.GEMINI_API_KEY:
            return "Error: GEMINI_API_KEY not set."

        genai.configure(api_key=Config.GEMINI_API_KEY)

        img = Image.open(image_file)
        model = genai.GenerativeModel(Config.GEMINI_OCR_MODEL)
        prompt = """
        You are a medical OCR extraction assistant.

        Extract all medical test details from this report image.

        For each test, return:

        - Test Name
        - Value
        - Unit
        - Reference Range (if available)

        Rules:
        - Return clean structured output
        - Do NOT explain anything
        - Do NOT add extra text
        - If something is missing, write "Not Available"

        Format:
        Test Name | Value | Unit | Reference Range

        Only output the table.
        """

        for _ in range(2):
            try:
                response = model.generate_content([prompt, img])

                if response:
                    return response.text
            except:
                continue

        return "Error: Gemini OCR failed."

    except Exception as e:
        return f"Error during OCR: {str(e)}"