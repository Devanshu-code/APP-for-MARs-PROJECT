# requirements.txt compatible setup included for Streamlit Cloud
# Ensure all needed packages are declared explicitly
# Add this content in a file named requirements.txt alongside this script:
#
# streamlit
# pdfplumber
# python-docx
# pytesseract
# transformers
# Pillow
# torch

import streamlit as st

try:
    import pdfplumber
except ModuleNotFoundError:
    st.error("Missing package 'pdfplumber'. Please add it to requirements.txt")
    st.stop()

try:
    import docx
except ModuleNotFoundError:
    st.error("Missing package 'python-docx'. Please add it to requirements.txt")
    st.stop()

try:
    from PIL import Image
except ModuleNotFoundError:
    st.error("Missing package 'Pillow'. Please add it to requirements.txt")
    st.stop()

try:
    import pytesseract
except ModuleNotFoundError:
    st.error("Missing package 'pytesseract'. Please add it to requirements.txt")
    st.stop()

try:
    from transformers import pipeline
except ModuleNotFoundError:
    st.error("Missing package 'transformers'. Please add it to requirements.txt")
    st.stop()

import os
import tempfile

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Extract text based on file type
def extract_text(file_path, file_type):
    if file_type == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    elif file_type == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_type in [".png", ".jpg", ".jpeg"]:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    elif file_type == ".txt":
        with open(file_path, 'r', encoding="utf-8") as f:
            return f.read()
    return None

# Generate structured metadata
def generate_metadata(text):
    short_text = text[:3000]
    summary = summarizer(short_text, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
    keywords = list(set(summary.lower().split()))
    metadata = {
        "Title": summary.split('.')[0],
        "Summary": summary,
        "Keywords": ", ".join(keywords[:10]),
        "Author": "Unknown",
        "Date": "Unknown"
    }
    return metadata

# Streamlit UI
st.title("Automated Metadata Generator")
st.write("Upload a document to extract text and generate metadata.")

uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

if uploaded_file:
    suffix = os.path.splitext(uploaded_file.name)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    text = extract_text(file_path, suffix)
    if text:
        st.subheader("Extracted Text")
        st.text_area("Content", text, height=200)

        metadata = generate_metadata(text)
        st.subheader("Generated Metadata")
        for key, value in metadata.items():
            st.markdown(f"**{key}:** {value}")
    else:
        st.error("Failed to extract text from the file.")
