import re

text = "KSH International Limited is a company. ICICI Securities and HDFC Bank are involved. Nuvama is also here."

pattern_company = r'\b([A-Z][A-Za-z0-9\.\&\-]*\s+(?:[A-Z][A-Za-z0-9\.\&\-]*\s+)*(?:Limited|Ltd\.?|Pvt\.?\s*Ltd\.?|Private Limited|LLP|Bank|Securities|Trust))\b'
for match in re.finditer(pattern_company, text):
    print("COMPANY Regex:", match.group(1).strip())
