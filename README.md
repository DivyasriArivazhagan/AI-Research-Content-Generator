# AI-Powered Research-to-Content Generation Agent Using Agentic RAG

## Project Overview

The AI-Powered Research-to-Content Generation Agent is an intelligent content creation system that uses Agentic Retrieval-Augmented Generation (RAG) to generate accurate and structured content from uploaded research documents.

Users can upload research documents in PDF, DOCX, PPTX, and TXT formats and provide a topic. The system retrieves relevant information from the uploaded documents, generates content using the NavigateLabs Nexus API, and verifies the generated content against the original source material.

The application helps reduce manual research effort and improves the relevance and reliability of AI-generated content.

## Key Features

- **Document Upload:** Supports PDF, DOCX, PPTX, and TXT files.
- **Text Extraction:** Extracts text from uploaded research documents.
- **Document Chunking:** Splits extracted text into smaller chunks for efficient retrieval.
- **Semantic Search:** Uses Sentence Transformers to identify relevant information.
- **Vector Database:** Stores document embeddings using ChromaDB.
- **Agentic RAG:** Uses multiple agents for research, retrieval, content generation, and verification.
- **AI Content Generation:** Generates structured content using NavigateLabs Nexus API.
- **Content Verification:** Identifies verified claims, unsupported claims, contradictions, and suggested corrections.
- **Source References:** Displays the original document names and chunk references.
- **Document Management:** Stores uploaded document information.
- **Generation History:** Maintains previously generated content.
- **Duplicate Detection:** Uses document hashing to identify duplicate uploads.

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask

### Artificial Intelligence
- Agentic RAG
- NavigateLabs Nexus API
- OpenAI Python SDK
- Sentence Transformers

### Database and Storage
- ChromaDB
- SQLite

### Document Processing
- PyMuPDF
- python-docx
- python-pptx

### Development Tools
- Visual Studio Code
- Git
- GitHub

## System Architecture

The application follows a sequential agent-based workflow.

1. **Document Processing:** Uploaded documents are processed and their text is extracted.
2. **Chunking:** Extracted text is divided into smaller chunks.
3. **Embedding Generation:** Sentence Transformers converts text chunks into vector embeddings.
4. **Vector Storage:** ChromaDB stores the embeddings for semantic retrieval.
5. **Research Agent:** Searches for relevant information based on the user's topic.
6. **Retrieval Agent:** Organizes the retrieved information and source references.
7. **Writer Agent:** Uses the NavigateLabs Nexus API to generate structured content.
8. **Verification Agent:** Checks generated claims against the retrieved source information.
9. **Output:** Displays the generated content, references, and verification report.

## Agent Workflow

**Research Agent**
- Identifies relevant research information from uploaded documents.
- Retrieves the top five relevant chunks.

**Retrieval Agent**
- Organizes the retrieved information.
- Collects source filenames and chunk numbers.

**Writer Agent**
- Generates blogs, research articles, and LinkedIn posts.
- Uses retrieved research information as the factual basis.

**Verification Agent**
- Checks whether claims are supported by source documents.
- Identifies unsupported claims and contradictions.
- Provides suggested corrections and a verification summary.

## Project Folder Structure

```text
Research_Content_Generator/
│
├── backend/
│   ├── __init__.py
│   ├── agents.py
│   ├── pdf_processor.py
│   └── rag_pipeline.py
│
├── generated_content/
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── uploads/
├── vector_db/
│
├── .env
├── .gitignore
├── app.py
├── database.py
├── README.md
├── requirements.txt
└── test_nexus.py
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/DivyasriArivazhagan/AI-Research-Content-Generator.git
```

### 2. Navigate to the Project Directory

```bash
cd Research_Content_Generator
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration:

```env
NEXUS_API_KEY=your_nexus_api_key
NEXUS_BASE_URL=https://nexusapi.navigatelabs.ai
```

Replace `your_nexus_api_key` with your actual NavigateLabs Nexus API key.

**Important:** Never upload your actual API key or `.env` file to GitHub.

### 7. Run the Application

```bash
python app.py
```

### 8. Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Requirements

The project dependencies are listed in `requirements.txt`.

Install them using:

```bash
python -m pip install -r requirements.txt
```

## Expected Output

The application provides:

- Uploaded research document details.
- Relevant retrieved research information.
- AI-generated content.
- Source document references.
- Verified claims.
- Unsupported claims.
- Contradictions.
- Suggested corrections.
- Verification summary.
- Previously generated content history.

## Future Enhancements

- Support for additional document formats.
- Improved claim-level verification.
- Advanced multi-agent orchestration.
- Export generated content as PDF and DOCX.
- Enhanced source citation and traceability.
- User authentication and access management.

## Repository

GitHub: https://github.com/DivyasriArivazhagan/AI-Research-Content-Generator

## Conclusion

This project demonstrates how Agentic RAG can combine document processing, semantic retrieval, AI-powered content generation, and source-based verification into a single application. It aims to make research-based content creation more efficient, structured, and reliable.
