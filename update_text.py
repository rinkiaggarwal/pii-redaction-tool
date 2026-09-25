import re

with open('app.py', 'r') as f:
    code = f.read()

old_text = """This application utilizes a Hybrid Deep Learning and Regex Engine alongside a Global 2-Pass Architecture to 
automatically detect and permanently obscure sensitive personally identifiable information across complex legal documents.
<br><br><i>Supports .docx and .pdf files.</i>"""

new_text = """Securely upload your legal and financial documents to automatically detect and permanently blackout sensitive personal information.
<br><br><i>Supports .docx and .pdf files.</i>"""

code = code.replace(old_text, new_text)

with open('app.py', 'w') as f:
    f.write(code)
