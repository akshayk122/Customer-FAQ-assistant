import os
import logging
from core.file_parser import load_faq_pairs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logger.info(f"Found {len(files)} files to process in {data_dir}")
    
    for file_path in files:
        try:
            logger.info(f"Processing file: {file_path}")
            faq_pairs = load_faq_pairs(file_path)
            logger.info(f"Extracted {len(faq_pairs)} FAQ entries from {file_path}")
            all_faqs.extend(faq_pairs)
        except Exception as e:
            logger.error(f"⚠️ Error parsing {file_path}: {e}")
    
    logger.info(f"Total FAQ entries loaded: {len(all_faqs)}")
    return all_faqs
