import streamlit as st
import os
import tempfile
from redactor import DocumentRedactor

st.set_page_config(
    page_title="PII Redaction Tool",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better styling in the Light theme with softer tones and button hover effects
st.markdown("""
    <style>
    .big-font {
        font-size: 28px !important;
        font-weight: 600;
        color: #D32F2F;
        margin-bottom: 10px;
        text-align: center;
    }
    .main-title {
        text-align: center;
    }
    /* Button Hover Effects */
    div.stButton > button {
        transition: all 0.3s ease;
        background-color: #D32F2F;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #B71C1C;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    /* Download Button Hover */
    div.stDownloadButton > button {
        transition: all 0.3s ease;
        background-color: #D32F2F;
        color: white;
        border: none;
    }
    div.stDownloadButton > button:hover {
        background-color: #B71C1C;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Secure PII Redaction Tool</h1>', unsafe_allow_html=True)
st.markdown("---")

# Initialize the redactor in session state to avoid reloading the DL model
if 'redactor' not in st.session_state:
    with st.spinner("Initializing Document Redaction Engine..."):
        st.session_state.redactor = DocumentRedactor()

st.markdown('<div class="big-font">Upload and Redact</div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
Securely upload your legal and financial documents to automatically detect and permanently blackout sensitive personal information.
<br><br><i>Supports .docx and .pdf files.</i>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Select a document to redact", type=["pdf", "docx"], label_visibility="collapsed")

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if st.button("Start Secure Redaction", use_container_width=True):
        with st.spinner("Traversing document and applying visual masks..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_in:
                tmp_in.write(uploaded_file.getvalue())
                input_path = tmp_in.name
            
            output_path = input_path.replace(f".{file_ext}", f"_redacted.{file_ext}")
            
            try:
                if file_ext == "docx":
                    st.session_state.redactor.redact_docx(input_path, output_path)
                elif file_ext == "pdf":
                    st.session_state.redactor.redact_pdf(input_path, output_path)
                
                st.session_state['redaction_done'] = True
                st.session_state['output_path'] = output_path
                st.session_state['uploaded_filename'] = uploaded_file.name
                st.session_state['report'] = st.session_state.redactor.get_report()
            except Exception as e:
                st.error(f"An error occurred: {e}")

# If Redaction is done, show the analytics!
if st.session_state.get('redaction_done'):
    st.markdown("---")
    st.markdown('<div class="big-font">Analytics and Report</div>', unsafe_allow_html=True)
    st.success("Redaction Completed Successfully")
    
    # Download Button
    with open(st.session_state['output_path'], "rb") as file:
        st.download_button(
            label="Download Redacted Document",
            data=file,
            file_name=f"redacted_{st.session_state['uploaded_filename']}",
            mime="application/octet-stream",
            use_container_width=True
        )
        
    st.markdown("### Entities Detected and Masked")
    report = st.session_state.get('report', {})
    if not report:
        st.info("No PII entities detected in this document.")
    else:
        keys = list(report.keys())
        for i in range(0, len(keys), 3):
            m_cols = st.columns(3)
            for j in range(3):
                if i + j < len(keys):
                    ent = keys[i+j]
                    m_cols[j].metric(label=ent, value=report[ent])
                    
st.markdown("---")
st.markdown('<h3 style="text-align: center;">Model Performance (148-Page Baseline)</h3>', unsafe_allow_html=True)
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

with st.expander("View How It Works"):
    st.markdown('''
    - **Pass 1 (Global Scan):** The intelligent scanner reads the entire document to detect all names, addresses, and phone numbers.
    - **Pass 2 (Global Replace):** Replaces all detected information with `██████` to guarantee 100% consistency across all paragraphs, headers, footers, and complex nested tables.
    ''')

# Cleanup temp files when a new file is uploaded
if not uploaded_file and st.session_state.get('redaction_done'):
    st.session_state['redaction_done'] = False
    if os.path.exists(st.session_state.get('output_path', '')):
        os.remove(st.session_state['output_path'])
