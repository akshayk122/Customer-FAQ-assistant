import os
import re
import json
import csv
import fitz  # PyMuPDF for PDFs
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt", ".csv", ".json"}

def get_all_supported_files(folder_path):
    """Returns a list of supported file paths from the given directory."""
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                all_files.append(os.path.join(root, file))
    return all_files

def is_question(line: str) -> bool:
    line = line.strip()
    return line.endswith('?') or bool(re.match(r'(?i)^(what|how|when|why|is|can|does|do|are|who|where)\b.*\?$', line))

def extract_faq_pairs(lines):
    """
    Extracts question-answer pairs from plain text lines.
    """
    faq_pairs = []
    question, answer = "", ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if is_question(line):
            if question and answer:
                faq_pairs.append({"question": question, "answer": answer.strip()})
            question = line
            answer = ""
        elif question:
            answer += line + " "
    
    if question and answer:
        faq_pairs.append({"question": question, "answer": answer.strip()})
    return faq_pairs

def load_docx(file_path):
    doc = DocxDocument(file_path)
    lines = [para.text for para in doc.paragraphs if para.text.strip()]
    return extract_faq_pairs(lines)

def load_pdf(file_path):
    doc = fitz.open(file_path)
    lines = []
    for page in doc:
        lines.extend(page.get_text().split('\n'))
    return extract_faq_pairs(lines)

def load_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return extract_faq_pairs(lines)

def load_csv(file_path):
    faq_pairs = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'question' in row and 'answer' in row:
                faq_pairs.append({
                    "question": row['question'].strip(),
                    "answer": row['answer'].strip()
                })
    return faq_pairs

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else []

def load_faq_pairs(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        return load_docx(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".txt":
        return load_txt(file_path)
    elif ext == ".csv":
        return load_csv(file_path)
    elif ext == ".json":
        return load_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def chunk_faqs(faq_list, file_name="unknown_file"):
    """
    Splits long answers into smaller semantic chunks with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = []
    for i, qa in enumerate(faq_list):
        question = qa.get("question", "")
        answer = qa.get("answer", "")
        for chunk in splitter.split_text(answer):
            chunks.append({
                "question": question,
                "chunk": chunk,
                "source": file_name,
                "doc_id": f"{file_name}__{i}"
            })
    return chunks
