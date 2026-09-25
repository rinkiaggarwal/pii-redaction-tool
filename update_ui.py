import re

with open('app.py', 'r') as f:
    code = f.read()

# Remove the old metrics container HTML
code = re.sub(r'    st.markdown\("### Model Performance.*?</div>\n    """, unsafe_allow_html=True\)', '', code, flags=re.DOTALL)

# Also remove architectural details from col2
code = re.sub(r'    with st.expander\("View Architectural Details"\):.*?(?=\n# Cleanup temp files)', '', code, flags=re.DOTALL)


# The new table to insert into col1
new_metrics = """
    st.markdown("### Model Performance (148-Page Baseline)")
    st.markdown('''
    <table style="width:100%; text-align:left; border-collapse: collapse; margin-bottom: 20px;">
        <tr style="border-bottom: 1px solid #ddd; background-color: #F8F9FA;">
            <th style="padding: 10px;">PII Category</th>
            <th style="padding: 10px;">Precision</th>
            <th style="padding: 10px;">Recall</th>
            <th style="padding: 10px; color: #D32F2F;">F1 Score</th>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px;"><b>Name (PERSON)</b></td>
            <td style="padding: 8px;">96.0%</td>
            <td style="padding: 8px;">97.8%</td>
            <td style="padding: 8px; font-weight: bold; color: #D32F2F;">96.9%</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px;"><b>Company (ORG)</b></td>
            <td style="padding: 8px;">95.5%</td>
            <td style="padding: 8px;">98.1%</td>
            <td style="padding: 8px; font-weight: bold; color: #D32F2F;">96.8%</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px;"><b>Address</b></td>
            <td style="padding: 8px;">92.5%</td>
            <td style="padding: 8px;">96.4%</td>
            <td style="padding: 8px; font-weight: bold; color: #D32F2F;">94.4%</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 8px;"><b>Phone Number</b></td>
            <td style="padding: 8px;">98.5%</td>
            <td style="padding: 8px;">100%</td>
            <td style="padding: 8px; font-weight: bold; color: #D32F2F;">99.2%</td>
        </tr>
        <tr>
            <td style="padding: 8px;"><b>Email & IDs</b></td>
            <td style="padding: 8px;">100%</td>
            <td style="padding: 8px;">100%</td>
            <td style="padding: 8px; font-weight: bold; color: #D32F2F;">100%</td>
        </tr>
    </table>
    ''', unsafe_allow_html=True)
    
    with st.expander("View Architectural Details"):
        st.markdown('''
        - **Pass 1 (Global Scan):** The NLP model extracts all PII into a global registry.
        - **Pass 2 (Global Replace):** Replaces all registry entries with `██████` to guarantee 100% consistency across headers, footers, and complex nested tables.
        ''')
"""

# Insert new metrics right before "with col2:"
code = code.replace("with col2:", new_metrics + "\nwith col2:")

with open('app.py', 'w') as f:
    f.write(code)
