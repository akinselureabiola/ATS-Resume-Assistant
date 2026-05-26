from pypdf import PdfReader
from docx import Document


# =========================
# PDF EXTRACTION
# =========================

def extract_text_from_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted + "\n"

    return text


# =========================
# DOCX EXTRACTION
# =========================

def extract_text_from_docx(file):

    doc = Document(file)

    text = []

    for paragraph in doc.paragraphs:

        text.append(
            paragraph.text
        )

    return "\n".join(text)


# =========================
# RESUME EXTRACTION
# =========================

def extract_resume_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    # TXT

    if file_name.endswith(".txt"):

        return uploaded_file.read().decode(
            "utf-8"
        )

    # PDF

    elif file_name.endswith(".pdf"):

        return extract_text_from_pdf(
            uploaded_file
        )

    # DOCX

    elif file_name.endswith(".docx"):

        return extract_text_from_docx(
            uploaded_file
        )

    return None


# =========================
# FILE SIZE VALIDATION
# =========================

def validate_file_size(
    uploaded_file,
    max_size_mb=5
):

    file_size_mb = (
        uploaded_file.size / 1024 / 1024
    )

    return file_size_mb <= max_size_mb