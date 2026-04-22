"""
Resume text extraction utilities.
Supports PDF and DOCX file formats.
"""

import io
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text content from a PDF file.

    Args:
        uploaded_file: Streamlit UploadedFile object (PDF).

    Returns:
        Extracted text as a single string.
    """
    uploaded_file.seek(0)  # Reset file pointer for re-reads
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(uploaded_file) -> str:
    """Extract all text content from a DOCX file.

    Args:
        uploaded_file: Streamlit UploadedFile object (DOCX).

    Returns:
        Extracted text as a single string.
    """
    uploaded_file.seek(0)  # Reset file pointer for re-reads
    doc = Document(io.BytesIO(uploaded_file.read()))
    text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(text_parts)


def extract_text(uploaded_file) -> str:
    """Extract text from a resume file based on its type.

    Args:
        uploaded_file: Streamlit UploadedFile object (PDF or DOCX).

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file format is not supported.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError(
            f"Unsupported file format: {filename}. Please upload a PDF or DOCX file."
        )
