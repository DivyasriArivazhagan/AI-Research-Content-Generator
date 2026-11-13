# AI-Powered Research-to-Content Generation Agent Using Agentic RAG

## 1. Project Overview

The AI-Powered Research-to-Content Generation Agent is an intelligent application that transforms uploaded research documents into structured, meaningful content using Retrieval-Augmented Generation (RAG) and multiple AI agents.

Users can upload research documents, enter a research topic, and generate content such as professional blogs, research articles, and LinkedIn posts. The system retrieves relevant information from uploaded documents and uses Gemini AI to generate and verify the content against the retrieved sources.

## 2. Key Features

- Upload PDF, DOCX, PPTX, and TXT documents.
- Extract text from uploaded research documents.
- Split extracted text into smaller chunks.
- Generate embeddings using Sentence Transformers.
- Store and retrieve document embeddings using ChromaDB.
- Detect duplicate document uploads.
- Retrieve relevant research information based on user queries.
- Generate content using Google Gemini API.
- Verify generated content against retrieved source material.
- Store document details and generation history using SQLite.
- Display supporting references and verification reports.
- Maintain document and generation history after page refresh.

## 3. AI Agent Architecture

### Research Agent
Analyzes the user's research topic and identifies relevant information from the stored research documents.

### Retrieval Agent
Retrieves relevant text chunks from ChromaDB and provides source information to the Writer Agent.

### Writer Agent
Uses Google Gemini to generate structured content based on the retrieved research information.

### Verification Agent
Checks generated content against the retrieved source material and identifies verified claims, unsupported claims, contradictions, and suggested corrections.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI Model | Google Gemini |
| RAG | Retrieval-Augmented Generation |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Database | SQLite |
| Document Processing | PyMuPDF, python-docx, python-pptx |

## 5. Project Structure

```text
Research_Content_Generator/
│
├── backend/
│   ├── __init__.py
│   ├── agents.py
│   ├── pdf_processor.py
│   └── rag_pipeline.py
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── uploads/
├── generated_content/
├── vector_db/
│
├── app.py
├── database.py
├── requirements.txt
├── research_content.db
├── .env
├── .gitignore
└── README.md
```

## 6. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Research_Content_Generator
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Gemini API Key

Create a `.env` file in the project root directory.

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own Google Gemini API key.

### Step 6: Run the Application

```bash
python app.py
```

Open the following URL in your browser:

```text
http://127.0.0.1:5000
```

## 7. Application Workflow

1. User uploads research documents.
2. The system extracts text from the documents.
3. Extracted text is divided into smaller chunks.
4. Sentence Transformers generates embeddings.
5. ChromaDB stores the embeddings and metadata.
6. User enters a research topic and selects a content type.
7. Research and Retrieval Agents retrieve relevant information.
8. Writer Agent generates content using Gemini.
9. Verification Agent checks the generated content against retrieved sources.
10. SQLite stores document metadata and generation history.

## 8. Supported Content Types

- Professional Blog
- Research Article
- LinkedIn Post

## 9. Databases Used

**ChromaDB:** Stores document embeddings, text chunks, and metadata for semantic retrieval.

**SQLite:** Stores uploaded document details and generated content history.

## 10. Security Notes

- Store API keys in the `.env` file.
- Do not upload API keys to GitHub.
- Add `.env`, `venv/`, and other sensitive or unnecessary files to `.gitignore`.

## 11. Future Enhancements

- Support additional document formats.
- Improve multi-agent orchestration.
- Add user authentication.
- Support multiple language generation.
- Improve source-grounded verification.
- Export generated content as PDF and DOCX.

## 12. Conclusion

This project combines Retrieval-Augmented Generation, vector databases, and AI agents to convert research documents into useful content. It helps users generate structured research-based content while providing supporting references and an AI-assisted verification report.
