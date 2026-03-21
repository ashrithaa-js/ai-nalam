import re

def format_percentage(value):
    """
    Format numeric values to percentages safely.
    """
    try:
        return f"{float(value)}%"
    except (ValueError, TypeError):
        return value

def extract_numbers(text):
    """
    Extract only numeric values from extraction results for visualization.
    """
    if not text:
        return None
    match = re.search(r"\d+\.?\d*", str(text))
    return float(match.group()) if match else None

def truncate_text(text: str, max_chars: int = 500):
    """
    Truncates text for previews using an ellipse.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
