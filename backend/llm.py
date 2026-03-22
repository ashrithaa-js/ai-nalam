import google.generativeai as genai
import json
import time
from backend.config import Config
from backend.logger import log_info, log_error, log_warning

# Configure the Gemini API
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GOOGLE_API_KEY)

def generate_response(prompt: str, retry_count: int = 3) -> str:
    """
    Generates a response from Gemini with Retry Logic for Rate Limiting.
    """
    # Model Names (Stable versions for your environment)
    # GEMINI_MODEL = "gemini-flash-latest"      # for text tasks
    # GEMINI_OCR_MODEL = "gemini-2.5-flash-image" # for OCR tasks
    for attempt in range(retry_count):
        try:
            model = genai.GenerativeModel(Config.GEMINI_MODEL)        
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                log_error("Gemini API returned an empty response.")
                return "Error: Empty response."
                
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = 40 + (attempt * 20)
                log_warning(f"Quota exceeded. Retrying in {wait_time}s... (Attempt {attempt+1}/{retry_count})")
                time.sleep(wait_time)
                continue
            log_error(f"Gemini API Error: {str(e)}")
            return f"Error: {str(e)}"
    
    return "Error: Quota exceeded after multiple retries."

def generate_unified_analysis(report_text: str, context: str = "", symptoms: str = "Not provided"):
    """
    🚀 NALAM SUPER-PIPELINE: ONE API CALL = 11 FEATURES
    Combines Risk, Score, Diet, Specialist, ELI5, etc. into a single JSON.
    """
    master_system_prompt = """
    ### 🛡️ MASTER SYSTEM PROMPT: NALAM MEDICAL INTELLIGENCE
    You are an AI medical assistant designed to help patients understand their lab reports.
    
    ### RULES:
    1. Do NOT diagnose diseases or suggest dosages.
    2. Use cautious language ("may indicate", "could suggest").
    3. Always recommend consulting a doctor.
    4. If data is unclear, say: "I am not fully certain based on the provided data."
    """

    task_prompt = f"""
    ### 📁 REPORT DATA:
    {report_text}
    
    ### 🔬 KNOWLEDGE CONTEXT:
    {context}
    
    ### 🤒 PATIENT SYMPTOMS:
    {symptoms}

    ### ⚡ TASK: Analyze the report and generate a SINGLE JSON object containing these 11 features:
    1.  **summary**: 1-2 sentence layman overview.
    2.  **risk_prediction**: {{level: "Low/Moderate/High", risks: [], reasoning: ""}}
    3.  **health_score**: {{score: 0-100, status: "Good/Moderate/Risk", reason: ""}}
    4.  **clinical_summary**: {{summary: "", impression: "", recommendations: []}}
    5.  **symptom_correlation**: Correlate symptoms with findings. If no symptoms, skip logic.
    6.  **follow_up**: {{suggestions: [], urgency: "Low/Med/High", reason: ""}}
    7.  **specialist_recommendation**: {{specialist: "", reason: "", when: ""}}
    8.  **eli5**: Very simple explanation for a child using analogies.
    9.  **error_detection**: Identify inconsistencies/issues in the report.
    10. **diet_plan**: {{breakfast: "", lunch: "", dinner: "", snacks: "", reason: ""}} (Use Indian/Tamil foods).
    11. **visuals**: List of entities for charts [{{test: "", value: "", normal_range: "", status: "low/normal/high"}}]

    Output ONLY VALID JSON.
    """

    full_prompt = f"{master_system_prompt}\n\n{task_prompt}"
    raw_response = generate_response(full_prompt)
    
    # Safety Check: Before parsing JSON
    if not raw_response or "Error" in raw_response:
        log_error(f"Analysis failed to generate content: {raw_response}")
        return { "error": "Analysis failed", "details": raw_response }

    try:
        # Enforce clean JSON parsing
        clean_json = raw_response.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        log_error(f"Failed to parse Unified Super JSON: {e}")
        return { "error": "JSON Parse Error", "raw": raw_response }

def chat_with_report(report_context: str, user_question: str):
    """
    Safe chatbot implementation for follow-up questions.
    """
    prompt = f"""
    You are a helpful and safe Medical Report Assistant.
    ### SAFETY: Avoid diagnosis. Refer to doctors.
    ### CONTEXT: {report_context}
    ### USER QUESTION: {user_question}
    """
    return generate_response(prompt)
