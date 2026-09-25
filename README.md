# Secure PII Redaction Tool

Welcome to the Secure PII Redaction Tool! This tool is built to automatically find and permanently redact sensitive Personal Identifiable Information (PII) from your `.docx` and `.pdf` documents.

## Why this tool?
Redacting documents manually is slow and prone to human error. This tool acts as an automated safety net. It uses a combination of structured rules and an advanced Artificial Intelligence (AI) language model to understand the context of your document and securely hide personal information.

Specifically, it is designed to handle complex Indian legal documents (like a Red Herring Prospectus).

## How it works (2-Pass Architecture)
This tool uses a powerful **2-Pass Architecture**:
1. **Pass 1 (Global Scanning):** It reads the entire document to detect PII using Regex (for structured formats like Emails, Phones, CIN, PAN, Aadhaar) and an AI Language Model (`spaCy en_core_web_lg`) for unstructured names, companies, and addresses. 
2. **Pass 2 (Global Replacement):** It generates a single mapping of Real Value -> Fake Value (e.g. "Sarthak Malvadkar" -> "John Doe"). It then scans the document a second time to replace EVERY occurrence of that value. This guarantees 100% consistency; if a name is caught once, it is redacted everywhere.

## Features
* **Realistic Substitutions:** It replaces PII with highly realistic fake values matching the original Indian locale context.
* **Complex Name Detection:** Pre-processes delimiter-separated lists (e.g. `Name1/ Name2/ Name3`) to catch clustered names that traditional AI models miss.
* **Corporate PII:** Includes specialized tracking for Company Names and Indian Corporate Identification Numbers (CIN).
* **Document Formatting Preserved:** For `.docx` files, it carefully replaces the text while keeping your tables, headers, and paragraph structures intact.

*Note on Unused Detectors: The codebase includes active detection mechanisms for Dates of Birth (DOB), IP Addresses, and Credit Card Numbers. A manual scan of the sample Red Herring Prospectus confirmed these data types were not present in this specific dataset, but the detectors remain active for generalizability.*

## Setup & Usage

### 1. Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_lg
```

### 2. Run the App
```bash
streamlit run app.py
```
