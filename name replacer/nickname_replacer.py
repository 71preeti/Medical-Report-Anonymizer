

import pytesseract
import spacy
import random
import gender_guesser.detector as gender
from PIL import Image
import fitz  # PyMuPDF
import os

# Set tesseract executable path (Windows only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load SpaCy model and gender detector
nlp = spacy.load("en_core_web_sm")
gender_detector = gender.Detector()

name_pools = {
    'indian': {
        'male': ['Ravi Mehta', 'Amit Kumar', 'Suresh Verma'],
        'female': ['Anjali Sharma', 'Neha Rani', 'Pooja Patel']
    },
    'muslim': {
        'male': ['Ahmed Raza', 'Imran Ali', 'Faisal Khan'],
        'female': ['Fatima Sheikh', 'Zainab Noor', 'Ayesha Bano']
    },
    'western': {
        'male': ['John Smith', 'Michael Brown', 'David Wilson'],
        'female': ['Emily Clark', 'Sophie Turner', 'Jessica Adams']
    },
    'chinese': {
        'male': ['Li Wei', 'Zhang Wei', 'Wang Jun'],
        'female': ['Chen Li', 'Mei Ling', 'Xiao Wen']
    },
    'african': {
        'male': ['Kwame Nkrumah', 'Samuel Okoro', 'Abdul Diallo'],
        'female': ['Amina Okafor', 'Fatou Bamba', 'Zahara Bello']
    }
}

def detect_region(name):
    name = name.lower()
    if any(x in name for x in ['khan', 'ahmed', 'fatima', 'zainab', 'ayesha']):
        return 'muslim'
    elif any(x in name for x in ['sharma', 'verma', 'kumar', 'ravi', 'pooja']):
        return 'indian'
    elif any(x in name for x in ['li', 'zhang', 'chen', 'xiao']):
        return 'chinese'
    elif any(x in name for x in ['kwame', 'amina', 'bamba', 'diallo']):
        return 'african'
    else:
        return 'western'

def detect_gender(name):
    g = gender_detector.get_gender(name.split()[0])
    return 'male' if g in ['male', 'mostly_male'] else 'female'

def extract_text_from_pdf(pdf_path):
    """Try normal text extraction, fallback to OCR if needed."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        text = page.get_text()
        if not text.strip():
            # Use OCR if page text is empty
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        full_text += text + "\n"
    return full_text

def process_file(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    text = ""
    fake_name_used = ""
    original_name_found = ""

    if ext == ".pdf":
        text = extract_text_from_pdf(input_path)
    else:
        img = Image.open(input_path).convert("RGB")
        text = pytesseract.image_to_string(img)

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            original_name_found = ent.text.strip()
            region = detect_region(original_name_found)
            gender = detect_gender(original_name_found)
            fake_name_used = random.choice(name_pools[region][gender])
            text = text.replace(original_name_found, fake_name_used, 1)
            break

    return text, original_name_found, fake_name_used
