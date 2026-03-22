import streamlit as st
import os
import sys
import tempfile

# Ensure the project root is in sys.path to find backend/ and prompts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pdf_parser import extract_text_from_pdf
from backend.ocr import extract_text_from_image
from backend.speech import speech_to_text, text_to_speech
from backend.rag import retrieve_context
from backend.llm import generate_unified_analysis, chat_with_report
from backend.logger import log_info, log_error

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Nalam AI", 
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NUCLEAR CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #f1f5f9; }

    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* GLOBAL BUTTON COLOUR FIX (FORCE OVERRIDE) */
    div[data-testid="stButton"] button {
        background-color: #1e3a8a !important; /* Deep Nalam Blue */
        color: white !important;              /* Bold White text */
        border: 2px solid #1e3a8a !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    /* BROWSE FILES & RESET BUTTON COLOUR FIX */
    div[data-testid="stFileUploader"] button,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background-color: #3b82f6 !important; /* Lighter Blue */
        border-color: #3b82f6 !important;
    }

    /* Standardized White Card */
    .card {
        background: white !important;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        color: #0f172a !important;
    }
    
    /* Scroll Box */
    .scroll-box {
        max-height: 250px;
        overflow-y: auto;
        background: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
        color: black !important;
        font-size: 0.88rem;
    }

    /* SideBar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827 !important; /* Darker Sidebar */
    }
    
    /* Sidebar chat messages compact */
    [data-testid="stSidebar"] .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px;
        padding: 5px;
        margin-bottom: 5px;
    }
    
    .health-score-container {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 50%;
        width: 135px;
        height: 135px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 8px solid #3b82f6;
        margin: auto;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=60)
    st.title("Nalam AI")
    st.markdown("<p style='font-size:0.80rem; opacity:0.6;'>v2.4 Platinum Edition</p>", unsafe_allow_html=True)
    
    # Reset Button Moved to the TOP
    if st.button("🗑️ Reset Data", use_container_width=True):
        st.session_state.extracted_text = ""
        st.session_state.analysis_results = None
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.subheader("💬 Ask Nalam AI")
    
    # Sidebar Chat Area
    with st.container(height=400, border=False):
        for chat in st.session_state['chat_history']:
            with st.chat_message(chat["role"]): 
                st.markdown(f"<span style='font-size:0.85rem;'>{chat['content']}</span>", unsafe_allow_html=True)
                
    if user_q := st.chat_input("Ask a follow up?👀"):
        st.session_state['chat_history'].append({"role": "user", "content": user_q})
        chat_context = str(st.session_state.analysis_results) if st.session_state.analysis_results else "No report."
        ans = chat_with_report(chat_context, user_q)
        st.session_state['chat_history'].append({"role": "assistant", "content": ans})
        st.rerun()

# --- HERO SECTION ---
st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧬 Nalam AI Assistant</h1>
        <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 0.2rem;">Professional Medical Analysis Powered by Super-LLM Pipeline</p>
        <p style="font-size: 0.93rem; opacity: 0.85; font-style: italic;">About: Nalam AI uses specialized Medical LLMs to simplify lab results.</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col_input, col_result = st.columns([1, 1.3], gap="large")

with col_input:
    st.subheader("Input📝")
    
    with st.container(border=True):
        tabs = st.tabs(["📄 PDF", "🖼️ Image", "🎙️ Voice", "✍️ Text"])
        with tabs[0]: up_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_plt", label_visibility="collapsed")
        with tabs[1]: up_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], key="img_plt", label_visibility="collapsed")
        with tabs[2]: up_vox = st.file_uploader("Upload Voice", type=["mp3", "wav"], key="vox_plt", label_visibility="collapsed")
        with tabs[3]: man_in = st.text_area("Report Input", height=100, label_visibility="collapsed")

    # Extraction Buttons
    bt_col1, bt_col2, bt_col3 = st.columns(3)
    with bt_col1:
        if up_pdf and st.button("Extract PDF", use_container_width=True):
            with st.spinner("..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(up_pdf.getbuffer())
                    st.session_state.extracted_text = extract_text_from_pdf(tmp.name)
    with bt_col2:
        if up_img and st.button("Extract Image", use_container_width=True):
            with st.spinner("..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(up_img.getbuffer())
                    st.session_state.extracted_text = extract_text_from_image(tmp.name)
    with bt_col3:
        if up_vox and st.button("Extract Audio", use_container_width=True):
             with st.spinner("..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(up_vox.getbuffer())
                    st.session_state.extracted_text = speech_to_text(tmp.name)

    # Scroll Box
    if st.session_state.extracted_text:
        st.markdown(f"""
            <div class="scroll-box">
                <b style="color:#1e3a8a;">Successfully Extracted Report Text:</b><br><br>
                {st.session_state.extracted_text}
            </div>
        """, unsafe_allow_html=True)

    st.subheader("🤒 Symptoms")
    symp_txt = st.text_area("Feelings?", placeholder="e.g., Tiredness...", height=80, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Analyse🤔", use_container_width=True):
        if not st.session_state.extracted_text:
            st.error("Please extract report data first.")
        else:
            with st.spinner("Analysing..."):
                try:
                    context = retrieve_context(st.session_state.extracted_text)
                    st.session_state.analysis_results = generate_unified_analysis(st.session_state.extracted_text, context, symp_txt)
                except Exception as e:
                    st.error(f"Analysis Failed: {e}")

with col_result:
    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        
        # Dashboard
        tp1, tp2 = st.columns([1, 2.2])
        with tp1:
            sc_info = res.get('health_score', {})
            sv = sc_info.get('score', 0)
            ss = sc_info.get('status', 'Unknown')
            scol = "#166534" if ss == "Good" else "#9a3412" if ss == "Moderate" else "#991b1b"
            st.markdown(f"""
                <div class="health-score-container" style="border-color: {scol};">
                    <span style="font-size: 0.72rem; color: #64748b; font-weight:bold;">SCORE</span>
                    <span style="font-size: 2.8rem; font-weight: bold; color: {scol}; line-height:1;">{sv}</span>
                    <span style="font-size: 0.85rem; font-weight: bold; color:{scol};">{ss.upper()}</span>
                </div>
            """, unsafe_allow_html=True)
        with tp2:
            st.markdown(f"<div class='card' style='padding: 1.2rem;'><b>Summary:</b><br>{res.get('summary', '')}</div>", unsafe_allow_html=True)
            r_pack = res.get('risk_prediction', {})
            st.warning(f"**Risk: {r_pack.get('level', 'Low')}** - {r_pack.get('reasoning', '')}")

        res_tabs = st.tabs(["🏥 Clinical", "🥗 Lifestyle", "👦 Patient Friendly", "🛠️ Audit"])

        with res_tabs[0]: # Clinical
            st.markdown("##### 🚩 Analysis findings")
            visuals = res.get('visuals', [])
            if visuals:
                cols = st.columns(3)
                for i, ent in enumerate(visuals):
                    stat = str(ent.get('status', 'normal')).lower()
                    with cols[i % 3]:
                        st.markdown(f"""
                            <div class="card" style="padding: 12px; margin-bottom: 8px; border-left: 5px solid #3b82f6;">
                                <b style='font-size:0.85rem; color:black;'>{ent.get('test')}</b><br>
                                <span style='font-size:1rem; color:#1e293b; font-weight:bold;'>{ent.get('value')} {ent.get('normal_range')}</span><br>
                                <small style='color:#64748b'>{stat.upper()}</small>
                            </div>
                        """, unsafe_allow_html=True)
            
            clin = res.get('clinical_summary', {})
            st.markdown(f"<div class='card'><b>Impression:</b><br>{clin.get('impression')}<br><br><b>Recommendations:</b><br>{', '.join(clin.get('recommendations', []))}</div>", unsafe_allow_html=True)
            
            spec = res.get('specialist_recommendation', {})
            st.markdown(f"<div class='card'><b>Recommended Specialist:</b> {spec.get('specialist')}<br><br><b>Reason:</b> {spec.get('reason')}</div>", unsafe_allow_html=True)

        with res_tabs[1]: # Lifestyle
            diet = res.get('diet_plan', {})
            st.markdown(f"""
                <div class='card'>
                    <b>🥗 Daily Diet Plan:</b><br>
                    🥚 <b>Breakfast:</b> {diet.get('breakfast')}<br>
                    🍲 <b>Lunch:</b> {diet.get('lunch')}<br>
                    ☕ <b>Snacks:</b> {diet.get('snacks')}<br>
                    🥣 <b>Dinner:</b> {diet.get('dinner')}<br><br>
                    <i><b>Rationale:</b> {diet.get('reason')}</i>
                </div>
            """, unsafe_allow_html=True)
            f_aud = res.get('follow_up', {})
            st.markdown(f"<div class='card'><b>🗓️ Follow-up Advice:</b><br>Urgency: {f_aud.get('urgency')}<br>Actions: {', '.join(f_aud.get('suggestions', []))}</div>", unsafe_allow_html=True)

        with res_tabs[2]: # Patient Friendly
            # VOICE BUTTON AT TOP FOR VISIBILITY
            if st.button("🔊 Tamil Voice Summary", use_container_width=True):
                 with st.spinner("Speaking in Tamil..."):
                    from backend.translation import english_to_tamil
                    ta_summary = english_to_tamil(res.get('summary'))
                    audio_path = text_to_speech(ta_summary, language='ta')
                    if audio_path: st.audio(audio_path, format="audio/wav")
            
            st.markdown(f"<div class='card'><b>👦 Explanation:</b><br>{res.get('eli5')}</div>", unsafe_allow_html=True)

        with res_tabs[3]: # Audit
            a_set = res.get('error_detection', {})
            a_msg = ""
            if isinstance(a_set, dict) and a_set.get('issues'):
                a_msg = f"<b>⚠️ Inconsistencies Detected:</b><br>{', '.join(a_set.get('issues'))}<br><br><b>Explanation:</b> {a_set.get('explanation')}"
            elif isinstance(a_set, str) and a_set.strip():
                a_msg = f"<b>AI Observation:</b><br>{a_set}"
            else:
                a_msg = "<b>✔️ Report Integrity:</b><br>No inconsistencies detected."
            st.markdown(f"<div class='card'>{a_msg}</div>", unsafe_allow_html=True)
            
    else:
        st.markdown("""
            <div style="text-align:center; padding: 6rem 2rem; opacity:0.3;">
                <h3>Nalam AI Dashboard</h3>
                <p>Upload a report to generate professional clinical insights.</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:1.1rem; font-weight:bold; color:white;'>⚠️Always consult a doctor. This is only for educational purpose❗</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:0.75em; opacity:0.5; color:black;'>Designed for Healthcare Literacy.</p>", unsafe_allow_html=True)
