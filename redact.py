import re
import random
from docx import Document
import spacy
from faker import Faker
import argparse
import sys
import logging

# Initialize Faker with Indian locale
fake = Faker('en_IN')
Faker.seed(42)  # For reproducible fakes, although mapping dictionary handles consistency

# A global dictionary to map real entities to fake entities consistently
entity_map = {}

# Constants for ignoring specific non-sensitive generic entities
IGNORE_ORGS = {
    "SEBI", "RBI", "ICICI Securities", "HDFC Bank", "BSE", "NSE", 
    "Ministry of Corporate Affairs", "MCA", "KSH International Limited",
    "KSH International", "Government of India", "State Bank of India"
}
# Feel free to add company CIN to avoid redacting the issuer's CIN
IGNORE_CINS = set()

# Regex patterns for specific PII types
REGEX_PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
    "PHONE": r'(?:\+91[\-\s]?)?[6-9]\d{9}\b|\+91[\-\s]?\d{2,4}[\-\s]?\d{6,8}\b',
    "PAN": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    "AADHAAR": r'\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b',
    "CIN": r'\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b',
    "CREDIT_CARD": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
    "IP_ADDRESS": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    "DOB": r'\b\d{2}[/-]\d{2}[/-]\d{4}\b' # simplistic dob pattern
}

def get_fake_value(entity_type, real_value):
    """
    Returns a consistent fake value for a given real value.
    """
    key = f"{entity_type}_{real_value}"
    if key in entity_map:
        return entity_map[key]

    if entity_type == "PERSON":
        fake_val = fake.name()
    elif entity_type == "ORG":
        fake_val = fake.company()
    elif entity_type == "GPE" or entity_type == "LOC":
        fake_val = fake.city() # or fake.address()
    elif entity_type == "EMAIL":
        fake_val = fake.ascii_company_email()
    elif entity_type == "PHONE":
        fake_val = "+91 " + fake.msisdn()[3:]
    elif entity_type == "PAN":
        # Fake PAN: 5 letters, 4 numbers, 1 letter
        fake_val = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5)) + \
                   "".join(random.choices("0123456789", k=4)) + \
                   random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    elif entity_type == "AADHAAR":
        fake_val = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif entity_type == "CIN":
        # Fake CIN format
        fake_val = random.choice(["L", "U"]) + \
                   "".join(random.choices("0123456789", k=5)) + \
                   "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2)) + \
                   str(random.randint(1900, 2023)) + \
                   "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3)) + \
                   "".join(random.choices("0123456789", k=6))
    elif entity_type == "CREDIT_CARD":
        fake_val = fake.credit_card_number()
    elif entity_type == "IP_ADDRESS":
        fake_val = fake.ipv4()
    elif entity_type == "DOB":
        fake_val = fake.date_of_birth().strftime("%d/%m/%Y")
    else:
        fake_val = f"[{entity_type}]"

    entity_map[key] = fake_val
    return fake_val


def detect_and_redact(text, nlp):
    """
    Detects PII in a given text using regex and spaCy, and replaces them.
    Because replacing modifies string length, we replace iteratively or backwards.
    """
    # 1. Regex Replacements
    # We apply regexes one by one
    for pii_type, pattern in REGEX_PATTERNS.items():
        matches = list(re.finditer(pattern, text))
        # Replace from end to start to avoid index shifting
        for match in reversed(matches):
            real_val = match.group()
            
            # Skip if it's an ignored CIN
            if pii_type == "CIN" and real_val in IGNORE_CINS:
                continue
                
            fake_val = get_fake_value(pii_type, real_val)
            text = text[:match.start()] + fake_val + text[match.end():]

    # 2. NER Replacements
    # Since text length changed, we need to rerun NLP on the partially redacted text
    doc = nlp(text)
    
    # Collect entities to redact (PERSON, ORG, GPE/LOC)
    # Ignore ignored orgs
    entities_to_replace = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
            # Check exclusions
            if ent.label_ == "ORG" and ent.text in IGNORE_ORGS:
                continue
            # Some basic filtering to avoid redacting common words mistagged
            if ent.text.lower() in ["offer", "ticket", "order", "page", "section"]:
                continue
            
            entities_to_replace.append((ent.start_char, ent.end_char, ent.label_, ent.text))
    
    # Sort backwards and replace
    entities_to_replace.sort(key=lambda x: x[0], reverse=True)
    for start, end, label, real_val in entities_to_replace:
        fake_val = get_fake_value(label, real_val)
        text = text[:start] + fake_val + text[end:]

    return text

def process_document(input_path, output_path):
    print(f"Loading spaCy model...")
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
        sys.exit(1)

    print(f"Reading document: {input_path}")
    try:
        doc = Document(input_path)
    except Exception as e:
        print(f"Error reading document: {e}")
        sys.exit(1)

    print(f"Processing {len(doc.paragraphs)} paragraphs...")
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            # To preserve formatting as much as possible at the run level,
            # replacing text in paragraphs is tricky if entities cross run boundaries.
            # For this tool, we will overwrite the paragraph text which might reset run formatting.
            # A more robust approach iterates through runs or uses python-docx's replace functionality,
            # but replacing full text is standard for baseline redaction.
            
            original_text = para.text
            redacted_text = detect_and_redact(original_text, nlp)
            
            if original_text != redacted_text:
                para.text = redacted_text
                
    # Note: To be thorough, we should also process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    original_text = cell.text
                    redacted_text = detect_and_redact(original_text, nlp)
                    if original_text != redacted_text:
                        cell.text = redacted_text

    print(f"Saving redacted document to: {output_path}")
    doc.save(output_path)
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PII Redaction Tool for Indian Regulatory Filings (RHP)")
    parser.add_argument("--input", required=True, help="Path to input .docx file")
    parser.add_argument("--output", default="redacted_output.docx", help="Path to save the redacted .docx file")
    
    args = parser.parse_args()
    process_document(args.input, args.output)
