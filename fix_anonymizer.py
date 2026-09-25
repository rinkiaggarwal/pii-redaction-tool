with open('redactor.py', 'r') as f:
    code = f.read()

new_func = """
    def get_fake_value(self, entity_type: str, real_value: str) -> str:
        if entity_type == "PERSON":
            return f"[{self.faker.name()}]"
        elif entity_type in ("GPE", "LOC", "ADDRESS"):
            return f"[{self.faker.address().replace(chr(10), ', ')}]"
        elif entity_type == "COMPANY":
            return f"[{self.faker.company()}]"
        elif entity_type == "EMAIL":
            return f"[{self.faker.ascii_company_email()}]"
        elif entity_type == "PHONE":
            return f"[+91 {self.faker.random_number(digits=10, fix_len=True)}]"
        elif entity_type == "PAN":
            return f"[{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{''.join(random.choices('0123456789', k=4))}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}]"
        elif entity_type == "AADHAAR":
            return f"[{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}]"
        elif entity_type == "CIN":
            return f"[{random.choice(['L', 'U'])}{random.randint(10000, 99999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{random.randint(1000, 9999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(100000, 999999)}]"
        elif entity_type == "CREDIT_CARD":
            return f"[{self.faker.credit_card_number()}]"
        elif entity_type == "IP_ADDRESS":
            return f"[{self.faker.ipv4()}]"
        elif entity_type == "DOB":
            return f"[{self.faker.date_of_birth().strftime('%d/%m/%Y')}]"
        return f"[Fake {entity_type}]"
"""

import re
code = re.sub(r'    def get_fake_value\(self, entity_type: str, real_value: str\) -> str:.*?(?=class DeepLearningPIIDetector:)', new_func + '\n', code, flags=re.DOTALL)

with open('redactor.py', 'w') as f:
    f.write(code)
