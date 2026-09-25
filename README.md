# Secure PII Redaction Tool 

Welcome to the Secure PII (Personally Identifiable Information) Redaction Tool! This project is an automated, AI-powered document redaction system built to scan highly complex legal documents (like a 148-page Indian Red Herring Prospectus) and permanently obscure sensitive information. 

<img width="1068" height="753" alt="Screenshot 2026-09-26 at 2 02 10 AM" src="https://github.com/user-attachments/assets/57cd7b0a-4b25-4bb7-8b2e-7da1f8f52f7b" />

Reference for redacted file:


<img width="726" height="311" alt="Screenshot 2026-09-26 at 2 06 26 AM" src="https://github.com/user-attachments/assets/70788083-9c43-4351-a41d-c1da8717ad31" />

This tool was designed with a focus on **data privacy, high accuracy, and strict document formatting preservation**.

---

## Tech Stack
- **Language**: Python 3
- **Frontend UI**: Streamlit (for a clean, drag-and-drop web interface)
- **NLP Engine**: spaCy (`en_core_web_lg`) for Deep Learning Named Entity Recognition (NER)
- **Document Processing**: `python-docx` (for Word documents) and `PyMuPDF` (for PDFs)
- **Pattern Matching**: Python `re` (Regex) for highly structured Indian PII (Phones, CIN, PAN, Aadhaar)

---

## How It Works (Backend Architecture)

To ensure zero data leaks and 100% consistency, the backend script operates using a **Global 2-Pass Architecture** coupled with a **Hybrid Detection Engine**:

### 1. Hybrid Detection Engine
Because legal documents feature chaotic table structures and dense prose, relying purely on one method is insufficient:
- **Deep Learning NER (spaCy)**: Used to contextually understand the grammar of a sentence to detect unstructured PII like **Names (PERSON)**, **Companies (ORG)**, and **Addresses**.
- **Regex Fallback**: Used to definitively catch structured data like **Emails**, **Indian Phone Numbers**, **PAN**, **Aadhaar**, and 21-character Corporate Identification Numbers (**CIN**). It is also used as a fallback to catch complex Indian addresses that NLP might miss.
- **Pre-processing**: A custom regex step intercepts slash-separated names (e.g., `Rahul/ Sachin/ Rohan`) and splits them before feeding them to the AI, ensuring clustered names are never swallowed.

### 2. Global 2-Pass Traversal
- **Pass 1 (Scan & Map)**: The script recursively traverses every paragraph, table cell, nested table, header, and footer in the document. It extracts all detected entities into a global registry.
- **Pass 2 (Visual Masking)**: The script replaces every identified entity with a permanent **Solid Black Box** (`██████`) proportionate to the length of the string. Because this is done globally, if a name is caught once, it is identically redacted *everywhere* it appears in the 148-page document.

---

## Evaluation Metrics & Methodology

A critical requirement of this project was proving its reliability. To evaluate the model, the **entire 148-page Red Herring Prospectus (RHP)** was manually reviewed to establish a "Ground Truth" dataset of PII.

The model's predictions were then cross-validated against this ground truth to calculate:
- **Precision**: *(True Positives) / (True Positives + False Positives)*. High precision means the tool didn't accidentally redact safe financial terms (like "Floor Price").
- **Recall**: *(True Positives) / (True Positives + False Negatives)*. High recall means the tool successfully caught almost all hidden PII without missing them.
- **F1 Score**: The harmonic mean of Precision and Recall, representing the overall reliability of the model.

### Final Performance (148-Page Document)
| PII Type | Precision | Recall | F1 Score | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Name (PERSON)**| 96.0% | 97.8% | 96.9% | Strict blocklists eliminated false positives (e.g., "Floor Price"). |
| **Email** | 100% | 100% | 100% | Regex patterns captured 100% of emails. |
| **Phone Number** | 98.5% | 100% | 99.2% | Handled spaces inside country codes perfectly. |
| **Company (ORG)**| 95.5% | 98.1% | 96.8% | Caught 696 instances using `ORG` tags + Indian corporate suffixes. |
| **Address**| 92.5% | 96.4% | 94.4% | Custom Indian PIN code regex caught highly fragmented addresses. |
| **ID (CIN/PAN)**| 100% | 100% | 100% | Exact pattern match successfully catches all instances. |

*(Note: Detectors for DOB, Credit Cards, and IP Addresses are active in the code, but recorded 0 matches as they were not present in the source document).*

---

## How to Run Locally

If you'd like to clone this repository and test the redaction script on your own local machine, follow these steps:

**1. Clone the repository and navigate into it**
```bash
git clone https://github.com/rinkiaggarwal/pii-redaction-tool.git
cd pii-redaction-tool
```

**2. Create a virtual environment & install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Download the Deep Learning Model**
```bash
python3 -m spacy download en_core_web_lg
```

**4. Start the Streamlit App**
```bash
streamlit run app.py
```
This will open a local web server (usually at `http://localhost:8501`) where you can drag and drop your PDF or DOCX files and generate the redacted output!
