import os
from core.file_parser import load_faq_pairs

SUPPORTED_EXTENSIONS = {'.docx', '.pdf', '.txt', '.csv', '.json'}

def get_all_files(data_dir):
    """
    Recursively collects all supported files in the given directory.
    """
    file_paths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                file_paths.append(os.path.join(root, file))
    return file_paths

def load_all_faqs(data_dir='sample_data'):
    """
    Load and combine all Q&A pairs from supported files in the given directory.
    """
    all_faqs = []
    files = get_all_files(data_dir)

    for file_path in files:
        try:
            faq_pairs = load_faq_pairs(file_path)
            all_faqs.extend(faq_pairs)
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")
    
    return all_faqs
