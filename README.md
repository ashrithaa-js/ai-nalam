# 🧬 Nalam AI Assistant

**"Empowering Healthcare Literacy through Intelligent Medical Analysis."**

Nalam AI is a professional medical report explainer designed to help users understand complex clinical lab results. Using a proprietary **Super-LLM Pipeline**, it extracts data from PDFs, Images, and Voice notes to provide a 360° health overview, including risk levels, personalized diet plans, and patient-friendly explanations.

---

## 🚀 Key Features

*   **⚡ Super-Pipeline Extraction**: One-click analysis that generates clinical impressions, risk scores, and specialist recommendations.
*   **🖼️ Advanced OCR & Parsing**: Robust extraction from medical images and PDFs using Google Gemini Vision.
*   **👦 Patient Friendly (ELI5)**: Simplifies complex terminology into analogies a child can understand.
*   **🔊 Tamil Voice Summary**: Integrated Tamil speech synthesis to make health data accessible.
*   **🥗 Personalized Lifestyle Plan**: Generates Indian/Tamil diet recommendations based on your report.
*   **💬 Intelligent Chatbot**: A safety-first medical assistant to answer follow-up questions.
*   **🔍 RAG Knowledge Base**: Uses a specialized medical vector store (FAISS + LangChain) for evidence-based context.

---

## 🛠️ Tech Stack

*   **Frontend**: Streamlit (Modern Medical UI)
*   **AI Engine**: Google Gemini (Flash & Pro)
*   **Vector Engine**: LangChain + FAISS (CPU)
*   **OCR**: Tesseract + Gemini Vision
*   **Speech**: Google TTS (gTTS) & Sarvam AI Integration
*   **Data Handling**: Python 3.12, PyMuPDF, pdfplumber

---

## 🍱 Project Structure

```text
├── frontend/
│   └── app.py              # Main Medical Dashboard
├── backend/
│   ├── llm.py              # Super-Pipeline Logic
│   ├── ocr.py              # Gemini Vision OCR
│   ├── rag.py              # Vector Store & Search
│   ├── speech.py           # TTS & Sound Processing
│   └── config.py           # System Environment
├── data/
│   ├── knowledge/          # Medical Reference Text
│   └── faiss_index/        # Pre-built Vector Store
└── requirements.txt        # High-Stability Dependencies
```

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/ashrithaa-js/ai-nalam.git
cd ai-nalam
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY = "your_key_here"
SARVAM_API_KEY = "your_key_here"
```

### 4. Run Locally
```bash
streamlit run frontend/app.py
```

---

## 🌐 Deployment (Streamlit Cloud)

1.  Push your code to GitHub.
2.  In Streamlit Cloud settings, specify **`frontend/app.py`** as the Main File.
3.  Add your **Secrets** in the Streamlit Dashboard using the key names above.
4.  The system will automatically use **`packages.txt`** to install Tesseract and Poppler.

---

## ⚠️ Disclaimer

**Educational Purpose Only.** Nalam AI is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider regarding your medical condition.

---

