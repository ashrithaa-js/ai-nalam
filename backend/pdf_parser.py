import pdfplumber
import re
from backend.logger import log_info, log_error

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and cleans all text from a PDF file using pdfplumber.
    Handles multi-page documents and removes unnecessary whitespace.
    """
    extracted_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    # Clean unnecessary whitespace and Normalize line breaks
                    cleaned_page = re.sub(r'\s+', ' ', page_text).strip()
                    extracted_text.append(cleaned_page)
        
        # Join pages with newlines for readability
        result = "\n\n".join(extracted_text) if extracted_text else "No text found in the PDF."
        log_info(f"PDF Extraction successful. Length: {len(result)}")
        return result

    except Exception as e:
        log_error(f"Error parsing PDF: {str(e)}")
        return f"Error parsing PDF: {str(e)}"
