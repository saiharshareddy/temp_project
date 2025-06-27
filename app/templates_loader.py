# app/templates_loader.py

import fitz  # PyMuPDF
from app.config import TEMPLATE_FOLDER

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def load_format_templates():
    return {
        1: extract_text_from_pdf(f"{TEMPLATE_FOLDER}/format1.pdf"),
        2: extract_text_from_pdf(f"{TEMPLATE_FOLDER}/format2.pdf")
    }
