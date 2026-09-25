import re
text = """
Telephone: +91 22 4009 4400
Telephone: + 91 20 45053237
Telephone: +91 81081 14949
Contact Rahul Dravid at rahul.d@gmail.com or call +91 9876543210.
His PAN is ABCDE1234F. Address is Mumbai.
"""
patterns = [
    r'(?i)(?:Telephone|Tel|Phone|Mob|Fax|Ph)[\s\:\.]*((?:\+|00)\s*91\s*)?[\d\s\-]{8,15}\b',
    r'(?:\+|00)\s*91\s*[\d\s\-]{8,15}\b',
    r'\b[6-9]\d{4}\s*[\-\.]?\s*\d{5}\b'
]
for p in patterns:
    print(f"Testing {p}")
    for m in re.finditer(p, text):
        print("  Matched:", m.group().strip())
