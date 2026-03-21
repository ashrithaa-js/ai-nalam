import requests
from backend.config import Config
from backend.logger import log_info, log_error

def english_to_tamil(text: str) -> str:
    """
    Translates English text to Tamil using Sarvam AI.
    """
    if not text:
        return ""
    return _call_sarvam_api(text, source_lang="en-IN", target_lang="ta-IN")

def tamil_to_english(text: str) -> str:
    """
    Translates Tamil text to English using Sarvam AI.
    """
    if not text:
        return ""
    return _call_sarvam_api(text, source_lang="ta-IN", target_lang="en-IN")

def _call_sarvam_api(text: str, source_lang: str, target_lang: str) -> str:
    """
    Internal helper to call Sarvam AI Translation API with chunking support.
    """
    if not Config.SARVAM_API_KEY:
        log_error("SARVAM_API_KEY not found in environment.")
        return text

    # Sarvam typically has a 1000-2000 character limit per request.
    MAX_CHARS = 1000
    if len(text) > MAX_CHARS:
        log_info(f"Splitting text of length {len(text)} into chunks for translation.")
        chunks = [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
        translated_chunks = []
        for chunk in chunks:
            translated_chunks.append(_execute_translation(chunk, source_lang, target_lang))
        return " ".join(translated_chunks)
    
    return _execute_translation(text, source_lang, target_lang)

def _execute_translation(text: str, source_lang: str, target_lang: str) -> str:
    url = f"{Config.SARVAM_TRANSLATE_URL}"
    headers = {
        "api-subscription-key": Config.SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": target_lang
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("translated_text", text)
    except Exception as e:
        log_error(f"Sarvam Translation Error: {e}")
        return text
