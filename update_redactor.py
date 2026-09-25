with open('redactor.py', 'r') as f:
    code = f.read()

# 1. Update Faker to visually mark the output with brackets e.g. [John Doe]
import re
code = re.sub(r'return self\.faker\.name\(\)', r'return f"[{self.faker.name()}]"', code)
code = re.sub(r'return self\.faker\.address\(\)\.replace\("\\n", ", "\)', r'return f"[{self.faker.address().replace(\'\\n\', \', \')}]"', code)
code = re.sub(r'return self\.faker\.company\(\)', r'return f"[{self.faker.company()}]"', code)
code = re.sub(r'return self\.faker\.ascii_company_email\(\)', r'return f"[{self.faker.ascii_company_email()}]"', code)
code = re.sub(r'return "\+91 " \+ str\(self\.faker\.random_number\(digits=10, fix_len=True\)\)', r'return f"[+91 {self.faker.random_number(digits=10, fix_len=True)}]"', code)
code = re.sub(r'return "".join\(random\.choices\("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5\)\) \+\s* "".join\(random\.choices\("0123456789", k=4\)\) \+\s* random\.choice\("ABCDEFGHIJKLMNOPQRSTUVWXYZ"\)', 
r'return f"[{''.join(random.choices(\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\', k=5))}{''.join(random.choices(\'0123456789\', k=4))}{random.choice(\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\')}]"', code)
code = re.sub(r'return f"\{random\.randint\(1000, 9999\)\} \{random\.randint\(1000, 9999\)\} \{random\.randint\(1000, 9999\)\}"', r'return f"[{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}]"', code)
code = re.sub(r'return random\.choice\(\[\'L\', \'U\'\]\) \+\s* str\(random\.randint\(10000, 99999\)\) \+\s* "".join\(random\.choices\("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2\)\) \+\s* str\(random\.randint\(1000, 9999\)\) \+\s* "".join\(random\.choices\("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3\)\) \+\s* str\(random\.randint\(100000, 999999\)\)',
r'return f"[{random.choice([\'L\', \'U\'])}{random.randint(10000, 99999)}{\'\'.join(random.choices(\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\', k=2))}{random.randint(1000, 9999)}{\'\'.join(random.choices(\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\', k=3))}{random.randint(100000, 999999)}]"', code)
code = re.sub(r'return self\.faker\.credit_card_number\(\)', r'return f"[{self.faker.credit_card_number()}]"', code)
code = re.sub(r'return self\.faker\.ipv4\(\)', r'return f"[{self.faker.ipv4()}]"', code)
code = re.sub(r'return self\.faker\.date_of_birth\(\)\.strftime\("%d/%m/%Y"\)', r'return f"[{self.faker.date_of_birth().strftime(\'%d/%m/%Y\')}]"', code)

# 2. Update docx traversal to include headers, footers, and nested tables
traversal_logic = """
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
"""

old_traversal = """        # PASS 2: REPLACE
        for para in doc.paragraphs:
            if para.text.strip():
                new_text = self._apply_redaction(para.text)
                if new_text != para.text:
                    style = para.style
                    para.text = new_text
                    para.style = style

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if para.text.strip():
                            new_text = self._apply_redaction(para.text)
                            if new_text != para.text:
                                style = para.style
                                para.text = new_text
                                para.style = style"""

code = code.replace(old_traversal, traversal_logic)

with open('redactor.py', 'w') as f:
    f.write(code)
