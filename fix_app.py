with open('app.py', 'r') as f:
    code = f.read()

# Fix the broken multiline string
import re
fixed_code = re.sub(r'st\.markdown\(\n\s*"- \*\*Name \(PERSON\).*?\)', 
'''st.markdown("""
- **Name (PERSON)**: 97.2% F1
- **Email/Phone/ID**: 99%+ F1
- **Company (ORG)**: 96.2% F1
- **Address**: 91.7% F1
""")''', code, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(fixed_code)
