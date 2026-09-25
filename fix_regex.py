with open('redactor.py', 'r') as f:
    code = f.read()

import re
new_dict = """    REGEX_PATTERNS = {
        "EMAIL": r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,7}\\b',
        "PHONE": r'(?i)(?:Telephone|Tel|Phone|Mob|Fax|Ph)[\\s\\:\\.]*((?:\\+|00)\\s*91\\s*)?[\\d\\s\\-]{8,15}\\b|(?:\\+|00)\\s*91\\s*[\\d\\s\\-]{8,15}\\b|\\b[6-9]\\d{4}\\s*[\\-\\.]?\\s*\\d{5}\\b',
        "PAN": r'\\b[A-Z]{5}[0-9]{4}[A-Z]{1}\\b',
        "ADDRESS": r'(?i)\\b(?:[A-Z0-9][A-Za-z0-9\\/\\-\\., ]{5,100}(?:Road|Street|Marg|Nagar|Colony|Ganj|Circle|Path|Zila|Bhavan|Estate|Park|Phase|Sector|Block|Apt|Building|Chowk)[A-Za-z0-9\\/\\-\\., ]{1,50}\\d{6})\\b',
        "AADHAAR": r'\\b\\d{4}[\\-\\s]?\\d{4}[\\-\\s]?\\d{4}\\b',
        "CIN": r'\\b[LU]\\d{5}[A-Z]{2}\\d{4}[A-Z]{3}\\d{6}\\b',
        "COMPANY": r'\\b([A-Z][A-Za-z0-9\\.\\&\\-]*\\s+(?:[A-Z][A-Za-z0-9\\.\\&\\-]*\\s+)*(?:Limited|Ltd\\.?|Pvt\\.?\\s*Ltd\\.?|Private Limited|LLP|Bank|Securities|Trust))\\b',
        "CREDIT_CARD": r'\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b',
        "IP_ADDRESS": r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b',
        "DOB": r'\\b\\d{2}[/-]\\d{2}[/-]\\d{4}\\b'
    }"""

code = re.sub(r'    REGEX_PATTERNS = \{.*?\n    \}', new_dict, code, flags=re.DOTALL)

with open('redactor.py', 'w') as f:
    f.write(code)
