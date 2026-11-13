import pymupdf as fitz
from docx import Document
from pptx import Presentation
import os


def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    text = ""

    # Extract PDF text
    if extension == ".pdf":

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text() + "\n"

        pdf.close()

    # Extract DOCX text
    elif extension == ".docx":

        document = Document(file_path)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    # Extract PPTX text
    elif extension == ".pptx":

        presentation = Presentation(file_path)

        for slide in presentation.slides:
            for shape in slide.shapes:

                if hasattr(shape, "text"):
                    text += shape.text + "\n"

    # Extract TXT text
    elif extension == ".txt":

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

    else:
        raise ValueError("Unsupported file format")

    return text.strip()
