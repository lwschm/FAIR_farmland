import os
import tempfile
from markitdown import MarkItDown
import streamlit as st

@st.cache_data(show_spinner=True)
def pdf_to_markdown(pdf_file):
    """
    Convert a PDF file to markdown text using MarkItDown.
    
    Args:
        pdf_file: The uploaded PDF file from Streamlit
        
    Returns:
        str: The extracted markdown text from the PDF
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, pdf_file.name)
        
        # Write the uploaded file to the temporary directory
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getvalue())
        
        # Initialize MarkItDown and convert the PDF
        md = MarkItDown()
        result = md.convert_local(temp_pdf_path)
        
        # Get the markdown text content
        markdown_text = result.text_content
        
        return markdown_text 