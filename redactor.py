import re
import random
from typing import List, Dict, Set
from dataclasses import dataclass
import fitz  # PyMuPDF
from docx import Document
import logging
from collections import defaultdict
import spacy
from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DetectedEntity:
    entity_type: str
    text: str
    start: int
    end: int

class PIIAnonymizer:
    def __init__(self):
        # The user requested realistic fake values using Faker with Indian locale
        self.faker = Faker('en_IN')



    def get_fake_value(self, entity_type: str, real_value: str) -> str:
        # The user requested to revert back to solid black visual masking!
        return "█" * len(real_value)

class DeepLearningPIIDetector:
    """
    Detects PII using a hybrid approach:
    1. spaCy en_core_web_lg for NER (Persons, Organizations, Locations).
    2. Regex for highly structured Indian PII.
    """
    REGEX_PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "PHONE": r'(?i)(?:Telephone|Tel|Phone|Mob|Fax|Ph)[\s\:\.]*((?:\+|00)\s*91\s*)?[\d\s\-]{8,15}\b|(?:\+|00)\s*91\s*[\d\s\-]{8,15}\b|\b[6-9]\d{4}\s*[\-\.]?\s*\d{5}\b',
        "PAN": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "ADDRESS": r'(?i)\b(?:[A-Z0-9][A-Za-z0-9\/\-\., ]{5,100}(?:Road|Street|Marg|Nagar|Colony|Ganj|Circle|Path|Zila|Bhavan|Estate|Park|Phase|Sector|Block|Apt|Building|Chowk)[A-Za-z0-9\/\-\., ]{1,50}\d{6})\b',
        "AADHAAR": r'\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b',
        "CIN": r'\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b',
        "COMPANY": r'\b([A-Z][A-Za-z0-9\.\&\-]*\s+(?:[A-Z][A-Za-z0-9\.\&\-]*\s+)*(?:Limited|Ltd\.?|Pvt\.?\s*Ltd\.?|Private Limited|LLP|Bank|Securities|Trust))\b',
        "CREDIT_CARD": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
        "IP_ADDRESS": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "DOB": r'\b\d{2}[/-]\d{2}[/-]\d{4}\b'
    }

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
        logger.info("Loading Deep Learning NER Model: spaCy en_core_web_lg")
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.info("Downloading en_core_web_lg...")
            import subprocess
            subprocess.run(["python3", "-m", "spacy", "download", "en_core_web_lg"], check=True)
            self.nlp = spacy.load("en_core_web_lg")

    def _process_delimited_names(self, text: str) -> List[DetectedEntity]:
        """Pre-processes text to extract slash/comma separated names."""
        entities = []
        pattern = r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\s*(?:[/,;]\s*[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)+)\b'
        for match in re.finditer(pattern, text):
            span_text = match.group(1)
            segments = re.split(r'[/,;]', span_text)
            current_idx = match.start(1)
            for seg in segments:
                seg_stripped = seg.strip()
                if seg_stripped:
                    doc = self.nlp(seg_stripped)
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            start_in_seg = seg.find(ent.text)
                            ent_start = current_idx + start_in_seg
                            ent_end = ent_start + len(ent.text)
                            entities.append(DetectedEntity("PERSON", ent.text, ent_start, ent_end))
                current_idx += len(seg) + 1
        return entities

    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # 0. Custom Delimited Names preprocessing
        entities.extend(self._process_delimited_names(text))

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
                elif ent.label_ == "ORG":
                    label = "COMPANY"
                else:
                    continue
                
                # Check against blocklist for PERSON (ignore for COMPANY)
                if label == "PERSON":
                    words = ent.text.split()
                    if any(word in self.BLOCKLIST for word in words):
                        continue
                    if len(ent.text) <= 2 or ent.text.replace(".", "").replace(",", "").isdigit():
                        continue
                
                entities.append(DetectedEntity(label, ent.text, ent.start_char, ent.end_char))

        return self._resolve_overlaps(entities)

    def _resolve_overlaps(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        entities.sort(key=lambda x: (x.start, -x.end))
        resolved = []
        last_end = -1
        for ent in entities:
            if ent.start >= last_end:
                resolved.append(ent)
                last_end = ent.end
        return resolved


class DocumentRedactor:
    """Handles global 2-pass redaction logic."""
    
    def __init__(self):
        self.detector = DeepLearningPIIDetector()
        self.anonymizer = PIIAnonymizer()
        self.entity_registry: Dict[str, str] = {} # real_text -> entity_type
        self.fake_mapping: Dict[str, str] = {}    # real_text -> fake_text
        self.entity_counts = defaultdict(int)

    def get_report(self) -> Dict[str, int]:
        return dict(self.entity_counts)

    def _scan_text(self, text: str):
        if not text.strip():
            return
        entities = self.detector.detect(text)
        for ent in entities:
            self.entity_registry[ent.text] = ent.entity_type

    def _build_fake_mapping(self):
        # Sort by length descending to prevent substring collisions
        sorted_keys = sorted(self.entity_registry.keys(), key=len, reverse=True)
        for real_text in sorted_keys:
            if real_text not in self.fake_mapping:
                entity_type = self.entity_registry[real_text]
                self.fake_mapping[real_text] = self.anonymizer.get_fake_value(entity_type, real_text)
                self.entity_counts[entity_type] += 1

    def _apply_redaction(self, text: str) -> str:
        if not text.strip():
            return text
        
        redacted_text = text
        # Because dict preserves insertion order (which is sorted by length descending)
        for real_text, fake_text in self.fake_mapping.items():
            if real_text in redacted_text:
                redacted_text = redacted_text.replace(real_text, fake_text)
        
        return redacted_text

    def redact_docx(self, input_path: str, output_path: str):
        logger.info(f"Redacting DOCX: {input_path}")
        self.entity_registry = {}
        self.fake_mapping = {}
        self.entity_counts = defaultdict(int)
        
        doc = Document(input_path)
        

        # PASS 1: SCAN
        for para in doc.paragraphs:
            self._scan_text(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._scan_text(para.text)
                    for nested_table in cell.tables:
                        for n_row in nested_table.rows:
                            for n_cell in n_row.cells:
                                for n_para in n_cell.paragraphs:
                                    self._scan_text(n_para.text)

        for section in doc.sections:
            for header in [section.header, section.first_page_header, section.even_page_header]:
                for para in header.paragraphs:
                    self._scan_text(para.text)
                for table in header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                self._scan_text(para.text)
            for footer in [section.footer, section.first_page_footer, section.even_page_footer]:
                for para in footer.paragraphs:
                    self._scan_text(para.text)
                for table in footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                self._scan_text(para.text)

                        
        # BUILD MAPPING
        self._build_fake_mapping()
        

        def _process_block(block):
            if hasattr(block, 'text') and block.text.strip():
                new_text = self._apply_redaction(block.text)
                if new_text != block.text:
                    style = block.style
                    block.text = new_text
                    block.style = style

        # PASS 2: REPLACE
        for para in doc.paragraphs:
            _process_block(para)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        _process_block(para)
                    for nested_table in cell.tables:
                        for n_row in nested_table.rows:
                            for n_cell in n_row.cells:
                                for n_para in n_cell.paragraphs:
                                    _process_block(n_para)

        for section in doc.sections:
            for header in [section.header, section.first_page_header, section.even_page_header]:
                for para in header.paragraphs:
                    _process_block(para)
                for table in header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                _process_block(para)
            for footer in [section.footer, section.first_page_footer, section.even_page_footer]:
                for para in footer.paragraphs:
                    _process_block(para)
                for table in footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                _process_block(para)

                        
        doc.save(output_path)
        logger.info(f"Saved redacted DOCX to: {output_path}")

    def redact_pdf(self, input_path: str, output_path: str):
        logger.info(f"Redacting PDF: {input_path}")
        self.entity_registry = {}
        self.fake_mapping = {}
        self.entity_counts = defaultdict(int)
        
        doc = fitz.open(input_path)
        
        # PASS 1: SCAN
        for page in doc:
            self._scan_text(page.get_text("text"))
            
        # BUILD MAPPING
        self._build_fake_mapping()
        
        # PASS 2: REPLACE (in PDF, we use PyMuPDF redaction annotations)
        for page in doc:
            for real_text, fake_text in self.fake_mapping.items():
                text_instances = page.search_for(real_text)
                for inst in text_instances:
                    page.add_redact_annot(inst, text=fake_text, cross_out=False)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            
        doc.save(output_path, garbage=4, deflate=True)
        logger.info(f"Saved redacted PDF to: {output_path}")
