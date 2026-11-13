
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

from backend.pdf_processor import extract_text

from backend.rag_pipeline import (
    split_text,
    store_chunks,
    retrieve_relevant_chunks,
    generate_document_hash
)

from backend.agents import run_agent_workflow

from database import (
    initialize_database,
    save_document,
    get_all_documents,
    save_generated_content,
    get_generation_history
)


app = Flask(__name__)

# ========================================
# CONFIGURATION
# ========================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLite database
initialize_database()


# ========================================
# CHECK ALLOWED FILE FORMATS
# ========================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ========================================
# HOME PAGE
# ========================================

@app.route("/")
def home():

    return render_template("index.html")


# ========================================
# STEP 1: UPLOAD DOCUMENTS
# ========================================

@app.route("/upload", methods=["POST"])
def upload_documents():

    if "files" not in request.files:

        return jsonify({
            "error": "No files selected"
        }), 400

    files = request.files.getlist("files")

    uploaded_files = []

    for file in files:

        if file.filename == "":
            continue

        if not allowed_file(file.filename):

            return jsonify({
                "error": f"Unsupported file format: {file.filename}"
            }), 400

        filename = secure_filename(file.filename)

        if not filename:

            return jsonify({
                "error": "Invalid filename"
            }), 400

        save_path = os.path.join(UPLOAD_FOLDER, filename)

        base, extension = os.path.splitext(filename)

        counter = 1

        while os.path.exists(save_path):

            filename = f"{base}_{counter}{extension}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1

        try:

            file.save(save_path)

            extracted_text = extract_text(save_path)

            if not extracted_text or not extracted_text.strip():

                raise ValueError("No readable text found")

            chunks = split_text(extracted_text)

            if not chunks:

                raise ValueError("Unable to create text chunks")

            # Generate document hash
            document_hash = generate_document_hash(chunks)

            # Store chunks in ChromaDB
            stored_count = store_chunks(chunks, filename)

            if stored_count == 0:

                if os.path.exists(save_path):
                    os.remove(save_path)

                uploaded_files.append({

                    "filename": filename,
                    "status": "Duplicate document detected",
                    "text_length": len(extracted_text),
                    "chunks_stored": 0

                })

            else:

                # Save document details in SQLite
                save_document(
                    filename,
                    document_hash,
                    len(extracted_text),
                    stored_count
                )

                uploaded_files.append({

                    "filename": filename,
                    "status": "Uploaded successfully",
                    "text_length": len(extracted_text),
                    "chunks_stored": stored_count

                })

        except Exception as error:

            if os.path.exists(save_path):
                os.remove(save_path)

            app.logger.exception(
                "Document processing failed: %s",
                filename
            )

            return jsonify({

                "error": f"Processing failed for {filename}: {str(error)}"

            }), 400

    if not uploaded_files:

        return jsonify({
            "error": "Please select at least one file"
        }), 400

    successful_count = sum(
        1 for item in uploaded_files
        if item["status"] == "Uploaded successfully"
    )

    duplicate_count = sum(
        1 for item in uploaded_files
        if item["status"] == "Duplicate document detected"
    )

    return jsonify({

        "message": "Document processing completed",
        "successful_uploads": successful_count,
        "duplicate_documents": duplicate_count,
        "files": uploaded_files

    }), 200


# ========================================
# STEP 2: GET SAVED DOCUMENTS
# ========================================

@app.route("/documents", methods=["GET"])
def documents():

    try:

        saved_documents = get_all_documents()

        return jsonify({

            "total_documents": len(saved_documents),
            "documents": saved_documents

        }), 200

    except Exception as error:

        app.logger.exception("Document retrieval failed")

        return jsonify({
            "error": str(error)
        }), 500


# ========================================
# STEP 3: RETRIEVE RESEARCH INFORMATION
# ========================================

@app.route("/retrieve", methods=["POST"])
def retrieve_documents():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "Invalid request data"
        }), 400

    topic = data.get("topic", "")

    if not isinstance(topic, str) or not topic.strip():

        return jsonify({
            "error": "Please enter a research topic"
        }), 400

    try:

        results = retrieve_relevant_chunks(
            topic.strip(),
            n_results=5
        )

        return jsonify({

            "message": "Retrieval successful",
            "topic": topic.strip(),
            "total_results": len(results),
            "results": results

        }), 200

    except Exception as error:

        app.logger.exception("Retrieval failed")

        return jsonify({
            "error": str(error)
        }), 500


# ========================================
# STEP 4: GENERATE CONTENT USING AI AGENTS
# ========================================

@app.route("/generate", methods=["POST"])
def generate_content():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "Invalid request data"
        }), 400

    topic = data.get("topic", "")
    content_type = data.get("content_type", "")

    if not isinstance(topic, str) or not topic.strip():

        return jsonify({
            "error": "Please enter a research topic"
        }), 400

    if not isinstance(content_type, str):

        return jsonify({
            "error": "Invalid content type"
        }), 400

    allowed_content_types = [
        "Professional Blog",
        "Research Article",
        "LinkedIn Post"
    ]

    if content_type not in allowed_content_types:

        return jsonify({
            "error": "Please select a valid content type"
        }), 400

    try:

        result = run_agent_workflow(
            topic.strip(),
            content_type
        )

        if result.get("status") != "success":

            return jsonify({

                "error": result.get(
                    "message",
                    "Content generation failed"
                )

            }), 500

        # Save generated content in SQLite
        save_generated_content(
            result["topic"],
            result["content_type"],
            result["generated_content"]
        )

        return jsonify({

            "message": "Content generated and verification completed",
            "topic": result["topic"],
            "content_type": result["content_type"],
            "generated_content": result["generated_content"],
            "sources": result["sources"],
            "verification": result["verification"]

        }), 200

    except Exception as error:

        app.logger.exception("Content generation error")

        return jsonify({
            "error": str(error)
        }), 500


# ========================================
# STEP 5: GET GENERATION HISTORY
# ========================================

@app.route("/history", methods=["GET"])
def history():

    try:

        saved_history = get_generation_history()

        return jsonify({

            "total_generations": len(saved_history),
            "history": saved_history

        }), 200

    except Exception as error:

        app.logger.exception("History retrieval failed")

        return jsonify({
            "error": str(error)
        }), 500


# ========================================
# FILE SIZE ERROR HANDLER
# ========================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "error": "File size exceeds the 20 MB limit"

    }), 413


# ========================================
# RUN FLASK APPLICATION
# ========================================

if __name__ == "__main__":

    app.run(debug=True)
