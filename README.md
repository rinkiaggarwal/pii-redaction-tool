# Secure PII Redaction Tool

Welcome to the Secure PII Redaction Tool! This tool is built to automatically find and permanently redact sensitive Personal Identifiable Information (PII) from your `.docx` and `.pdf` documents.

## Why this tool?
Redacting documents manually is slow and prone to human error. This tool acts as an automated safety net. It uses a combination of structured rules and an advanced Artificial Intelligence (AI) language model to understand the context of your document and securely hide personal information.

Specifically, it is designed to handle complex Indian legal documents (like a Red Herring Prospectus) where text isn't in neat rows, but scattered throughout paragraphs and tables.

## How it works
This tool uses a "Hybrid Approach" to detect PII:
1. **Rule-based Matching (Regex):** For data that follows a strict, predictable format (like Emails, Phone Numbers, Aadhaar, PAN, Credit Cards, IP Addresses, and Dates of Birth), the tool uses exact pattern matching. This guarantees 100% detection for these types.
2. **AI Language Model (spaCy NLP):** Names, Addresses, and Organizations do not follow strict patterns. "John Doe" and "Mumbai" look like regular words. To solve this, the tool uses a pre-trained AI Natural Language Processing (NLP) model (`spaCy`). This model reads the grammar and context of the sentence to figure out if a word is a person's name or a physical address. 
   - *Note on Precision:* Pure rule-based matching is impossible for names without creating thousands of false positives (like redacting every capitalized word). The AI model allows us to specifically target individuals (Directors, Officers) while safely ignoring corporate entities and financial terms (like "KSH International Limited" or "Floor Price").

## Features
* **Visual Masking & Permanent Deletion:** It doesn't just replace data with fake text; it applies true **Solid Black Box Visual Masking** (`██████████`). This permanently erases the underlying data so it cannot be copy-pasted or recovered, matching the industry standard for redaction.
* **Document Formatting Preserved:** For `.docx` files, it carefully replaces the text while keeping your tables, headers, and paragraph structures intact. No messy blocks of text!

## Setup & Usage

### 1. Installation
Open your terminal and run the following commands:
```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required libraries
pip install -r requirements.txt

# Download the AI language model
python3 -m spacy download en_core_web_sm
```

### 2. Run the App
Launch the web interface:
```bash
streamlit run app.py
```
This will open a friendly web page where you can drag-and-drop your documents, view a report of what was removed, and download your clean, visually masked, and safe file!
