import re
import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text

def chunk_by_article(text: str) -> list:
    # Split by "አንቀጽ" (works for both Arabic and Amharic numerals)
    pattern = r'(አንቀጽ\s+\d+|[፩-፱]+\s*አንቀጽ)'
    sections = re.split(pattern, text)
    chunks = []
    for i in range(1, len(sections), 2):
        article_title = sections[i] if i < len(sections) else "Unknown"
        article_body = sections[i+1] if i+1 < len(sections) else ""
        chunks.append({
            "title": article_title.strip(),
            "text": (article_title + " " + article_body).strip()
        })
    return chunks