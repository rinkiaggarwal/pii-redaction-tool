with open('redactor.py', 'r') as f:
    code = f.read()

scan_logic = """
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
"""

old_scan = """        # PASS 1: SCAN
        for para in doc.paragraphs:
            self._scan_text(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._scan_text(para.text)"""

code = code.replace(old_scan, scan_logic)

with open('redactor.py', 'w') as f:
    f.write(code)
