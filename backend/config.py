import os
from dotenv import load_dotenv

# Load all environment variables once
load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

    # Model Names (Directly following your stable environment logic)
    GEMINI_MODEL = "gemini-flash-latest"      # Optimized text model
    GEMINI_OCR_MODEL = "gemini-2.5-flash-image" # Specialized OCR model
    
    # Path Configurations
    KNOWLEDGE_DIR = "data/knowledge/"
    RAW_DATA_DIR = "data/raw/"
    PROCESSED_DATA_DIR = "data/processed/"
    VECTOR_STORE_PATH = "data/faiss_index"

    # Sarvam AI Specifics
    SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
    SARVAM_ASR_URL = "https://api.sarvam.ai/speech-to-text"
    SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
    
    # Fixed TTS Settings
    DEFAULT_SPEAKER = "anushka"
    TTS_MODEL = "bulbul:v2"
