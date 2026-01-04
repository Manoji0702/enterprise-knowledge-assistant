from pypdf import PdfReader
from docx import Document
import os

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_md(path):
    return extract_text_from_txt(path)

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        return extract_text_from_txt(path)
    if ext == ".md":
        return extract_text_from_md(path)
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)

    raise ValueError("Unsupported file format")
