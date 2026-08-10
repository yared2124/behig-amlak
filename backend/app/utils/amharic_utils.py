import re

def normalize_amharic(text: str) -> str:
    # Standardize spaces around punctuation
    text = re.sub(r'\s*[፡።፤፥፦]\s*', lambda m: m.group(0).strip(), text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_ocr_artifacts(text: str) -> str:
    # Remove common OCR noise (e.g., page numbers, stray chars)
    text = re.sub(r'[0-9]+\s*of\s*[0-9]+', '', text, flags=re.IGNORECASE)
    return text