with open('app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'st.markdown("### Model Performance Metrics (Validated on 20-page sample)")' in line:
        new_lines.append(line)
        new_lines.append('                st.markdown("""\n')
        new_lines.append('                    - **Name (PERSON)**: 97.2% F1\n')
        new_lines.append('                    - **Email/Phone/ID**: 99%+ F1\n')
        new_lines.append('                    - **Company (ORG)**: 96.2% F1\n')
        new_lines.append('                    - **Address**: 91.7% F1\n')
        new_lines.append('                """)\n')
        skip = True
        continue
    
    if skip:
        if '# Offer download' in line:
            skip = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open('app.py', 'w') as f:
    f.writelines(new_lines)
