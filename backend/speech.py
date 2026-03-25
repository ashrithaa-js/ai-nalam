import requests
import os
import base64
import tempfile
from backend.config import Config
from backend.logger import log_info, log_error
from sarvamai import SarvamAI


def speech_to_text(audio_file_path: str) -> str:
    try:
        api_key = os.getenv("SARVAM_API_KEY")

        if not api_key:
            return "Error: SARVAM_API_KEY not set."

        client = SarvamAI(api_subscription_key=api_key)

        response = client.speech_to_text.transcribe(
            file=open(audio_file_path, "rb"),
            model="saarika:v2.5"
        )

        return response.transcript

    except Exception as e:
        log_error(f"Speech-to-Text error: {e}")
        return f"Error transcribing audio: {str(e)}"

def text_to_speech(text: str, language: str = 'ta') -> str:
    """
    Converts text to speech using Sarvam AI TTS (v2 payload).
    """
    if not Config.SARVAM_API_KEY:
        log_error("SARVAM_API_KEY missing.")
        return None

    # SAFETY: Trim text to avoid 400 Bad Request
    text_to_process = text[:500] 

    url = Config.SARVAM_TTS_URL
    headers = {
        "api-subscription-key": Config.SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Payload format FIXED for bulbul:v2
    payload = {
        "text": text_to_process,
        "target_language_code": "ta-IN" if language == 'ta' else "en-IN",
        "speaker": Config.DEFAULT_SPEAKER,
        "model_id": Config.TTS_MODEL
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            log_error(f"Sarvam TTS Failed ({response.status_code}): {response.text}")
            return None
            
        audio_data = response.json().get("audios", [])
        if not audio_data:
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(base64.b64decode(audio_data[0]))
            return tmp.name

    except Exception as e:
        log_error(f"Text-to-Speech error: {e}")
        return None
