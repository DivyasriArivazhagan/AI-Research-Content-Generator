
from backend.pdf_processor import extract_text
from backend.rag_pipeline import split_text, store_chunks, collection

import os

folder = "uploads"

files = [
    file for file in os.listdir(folder)
    if file.lower().endswith((".pdf", ".docx", ".pptx", ".txt"))
]

if not files:
    print("No documents found.")

else:
    filename = files[0]
    file_path = os.path.join(folder, filename)

    # Step 1: Extract text
    text = extract_text(file_path)

    print("Document:", filename)
    print("Extracted text length:", len(text))

    # Step 2: Split text
    chunks = split_text(text)

    print("Total chunks:", len(chunks))

    # Step 3: Store in ChromaDB
    stored_count = store_chunks(chunks, filename)

    print("Stored chunks:", stored_count)
    print("ChromaDB total records:", collection.count())

    print("\nChromaDB storage successful!")
