import re
from typing import List, Dict
from dataclasses import dataclass
import fitz  # PyMuPDF
from docx import Document
import logging
from collections import defaultdict
import spacy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DetectedEntity:
    entity_type: str
    text: str
    start: int
    end: int

class PIIAnonymizer:
    def get_fake_value(self, entity_type: str, real_value: str) -> str:
        """Returns a solid black block for visual masking and permanent deletion."""
        # The user requested 'Visual Masking: typically places a solid black box'
        # We replace the text with the '█' block character, matching the exact length of the original text.
        # This completely erases the underlying data while visually looking like a blackout redaction.
        return '█' * len(real_value)

class DeepLearningPIIDetector:
    """
    Detects PII using a hybrid approach:
    1. Deep Learning NER (spaCy en_core_web_sm) for complex NER (Persons, Locations).
    2. Regex for highly structured Indian PII (Aadhaar, PAN, Phone, Email, etc.).
    """
    REGEX_PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "PHONE": r'(?:\+91[\-\s]?)?[6-9]\d{9}\b|\+91[\-\s]?\d{2,4}[\-\s]?\d{6,8}\b',
        "PAN": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "AADHAAR": r'\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b',
        "CREDIT_CARD": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
        "IP_ADDRESS": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "DOB": r'\b\d{2}[/-]\d{2}[/-]\d{4}\b'
    }

    # Blocklist to prevent False Positives common in Indian Financial/IPO Documents
    BLOCKLIST = {
        "Floor", "Cap", "Price", "Fresh", "Issue", "Offer", "Sale", "Company", "Trust", 
        "Limited", "Bank", "BSE", "NSE", "SEBI", "RBI", "ICICI", "Securities", "Private",
        "Pvt", "Ltd", "Equity", "Shares", "Amount", "Size", "Million", "Billion", "Rupees",
        "INR", "Value", "Capital", "Net", "Proceeds", "Average", "Cost", "Acquisition",
        "Weighted", "Promoter", "Selling", "Shareholder", "QIBs", "NIIs", "RIIs",
        "Deen", "Dayal", "Upadhyaya", "Gram", "Jyoti", "Atal", "Mission", "Pradhan", 
        "Mantri", "Awas", "Yojana", "Scheme", "National", "State", "Central", "Government",
        "India", "Maharashtra", "Pune", "Mumbai", "Delhi", "Book", "Building", "Process",
        "Red", "Herring", "Prospectus", "Draft", "DRHP", "RHP", "IPO"
    }

    def __init__(self):
        logger.info("Loading Deep Learning NER Model: spaCy en_core_web_sm")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading en_core_web_sm...")
            import subprocess
            subprocess.run(["python3", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")

    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # 1. Regex Detection
        for entity_type, pattern in self.REGEX_PATTERNS.items():
            for match in re.finditer(pattern, text):
                entities.append(DetectedEntity(entity_type, match.group(), match.start(), match.end()))

        # 2. Deep Learning NER Detection
        if text.strip():
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    label = "PERSON"
                elif ent.label_ in ["GPE", "LOC", "FAC"]:
                    label = "ADDRESS"
                else:
                    continue  # Ignore ORG and others as requested
                
                # Check against blocklist
                words = ent.text.split()
                if any(word in self.BLOCKLIST for word in words):
                    continue
                    
                # Skip things that look like pure numbers or very short
                if len(ent.text) <= 2 or ent.text.replace(".", "").replace(",", "").isdigit():
                    continue
                
                entities.append(DetectedEntity(label, ent.text, ent.start_char, ent.end_char))

        # Filter overlapping entities (Regex takes precedence over NER if overlap exists)
        return self._resolve_overlaps(entities)

    def _resolve_overlaps(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Resolves overlapping entity spans by prioritizing longer spans or specific types."""
        entities.sort(key=lambda x: (x.start, -x.end))
        resolved = []
        last_end = -1
        for ent in entities:
            if ent.start >= last_end:
                resolved.append(ent)
                last_end = ent.end
        return resolved


class DocumentRedactor:
    """Handles parsing and redacting different document formats (.docx, .pdf)."""
    
    def __init__(self):
        self.detector = DeepLearningPIIDetector()
        self.anonymizer = PIIAnonymizer()
        self.entity_counts = defaultdict(int)

    def get_report(self) -> Dict[str, int]:
        """Returns the count of redacted entities."""
        return dict(self.entity_counts)

    def reset_report(self):
        self.entity_counts = defaultdict(int)

    def _redact_text(self, text: str) -> str:
        """Redacts a single string of text and updates counts."""
        entities = self.detector.detect(text)
        
        for ent in entities:
            self.entity_counts[ent.entity_type] += 1

        # Sort in reverse order to prevent index shifting during replacement
        entities.sort(key=lambda x: x.start, reverse=True)
        
        redacted_text = text
        for ent in entities:
            fake_val = self.anonymizer.get_fake_value(ent.entity_type, ent.text)
            redacted_text = redacted_text[:ent.start] + fake_val + redacted_text[ent.end:]
            
        # Clean up anomalies like double spaces
        redacted_text = re.sub(r' +', ' ', redacted_text)
        return redacted_text

    def _redact_paragraph(self, para):
        """Redacts a paragraph while attempting to preserve its base style."""
        if not para.text.strip():
            return
        
        original_text = para.text
        redacted_text = self._redact_text(original_text)
        
        if original_text != redacted_text:
            style = para.style
            para.text = redacted_text
            para.style = style

    def redact_docx(self, input_path: str, output_path: str):
        """Redacts a Word document preserving structure."""
        logger.info(f"Redacting DOCX: {input_path}")
        self.reset_report()
        doc = Document(input_path)
        
        # Redact paragraphs
        for para in doc.paragraphs:
            self._redact_paragraph(para)
                
        # Redact tables safely (iterating over paragraphs inside cells to prevent flattening)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._redact_paragraph(para)
                        
        doc.save(output_path)
        logger.info(f"Saved redacted DOCX to: {output_path}")

    def redact_pdf(self, input_path: str, output_path: str):
        """
        Redacts a PDF using PyMuPDF (fitz). 
        Draws black redaction annotations or replaces text directly where supported.
        """
        logger.info(f"Redacting PDF: {input_path}")
        self.reset_report()
        doc = fitz.open(input_path)
        
        for page in doc:
            text = page.get_text("text")
            entities = self.detector.detect(text)
            
            for ent in entities:
                self.entity_counts[ent.entity_type] += 1
                text_instances = page.search_for(ent.text)
                for inst in text_instances:
                    # Draw a black redaction box and remove underlying text
                    # We pass text=' ' to ensure it doesn't just replace text, but visually masks it
                    page.add_redact_annot(inst, fill=(0, 0, 0), cross_out=False)
            
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            
        doc.save(output_path, garbage=4, deflate=True)
        logger.info(f"Saved redacted PDF to: {output_path}")

