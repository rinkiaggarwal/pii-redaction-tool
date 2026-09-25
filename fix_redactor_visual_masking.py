with open('redactor.py', 'r') as f:
    code = f.read()

new_func = """
    def get_fake_value(self, entity_type: str, real_value: str) -> str:
        # The user requested to revert back to solid black visual masking!
        return "█" * len(real_value)
"""

import re
code = re.sub(r'    def get_fake_value\(self, entity_type: str, real_value: str\) -> str:.*?(?=class DeepLearningPIIDetector:)', new_func + '\n', code, flags=re.DOTALL)

# Add the ADDRESS fallback regex to DeepLearningPIIDetector
address_regex = r'"ADDRESS": r\'(?i)\\b(?:[A-Z0-9][A-Za-z0-9\/\-\., ]{5,100}(?:Road|Street|Marg|Nagar|Colony|Ganj|Circle|Path|Zila|Bhavan|Estate|Park|Phase|Sector|Block|Apt|Building|Chowk)[A-Za-z0-9\/\-\., ]{1,50}\\d{6})\\b\','
code = re.sub(r'"AADHAAR":', address_regex + '\n        "AADHAAR":', code)

with open('redactor.py', 'w') as f:
    f.write(code)
