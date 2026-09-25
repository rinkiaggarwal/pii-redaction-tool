import re

with open('app.py', 'r') as f:
    code = f.read()

old_expander = """with st.expander("View Architectural Details"):
    st.markdown('''
    - **Pass 1 (Global Scan):** The NLP model extracts all PII into a global registry.
    - **Pass 2 (Global Replace):** Replaces all registry entries with `██████` to guarantee 100% consistency across headers, footers, and complex nested tables.
    ''')"""

new_expander = """with st.expander("View How It Works"):
    st.markdown('''
    - **Pass 1 (Global Scan):** The intelligent scanner reads the entire document to detect all names, addresses, and phone numbers.
    - **Pass 2 (Global Replace):** Replaces all detected information with `██████` to guarantee 100% consistency across all paragraphs, headers, footers, and complex nested tables.
    ''')"""

code = code.replace(old_expander, new_expander)

with open('app.py', 'w') as f:
    f.write(code)
