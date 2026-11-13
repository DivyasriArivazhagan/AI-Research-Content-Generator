
import sqlite3
import os

# Database file location
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "research_content.db"
)


# ========================================
# CONNECT TO DATABASE
# ========================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ========================================
# CREATE DATABASE TABLES
# ========================================

def initialize_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    # Uploaded documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_hash TEXT,
            text_length INTEGER,
            chunks_stored INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Generated content history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content_type TEXT NOT NULL,
            generated_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()

    print("SQLite database initialized successfully.")


# ========================================
# SAVE UPLOADED DOCUMENT
# ========================================

def save_document(
    filename,
    document_hash,
    text_length,
    chunks_stored
):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO documents (
            filename,
            document_hash,
            text_length,
            chunks_stored
        )
        VALUES (?, ?, ?, ?)
    """, (
        filename,
        document_hash,
        text_length,
        chunks_stored
    ))

    connection.commit()

    connection.close()


# ========================================
# GET ALL UPLOADED DOCUMENTS
# ========================================

def get_all_documents():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM documents
        ORDER BY uploaded_at DESC
    """)

    documents = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return documents


# ========================================
# SAVE GENERATED CONTENT
# ========================================

def save_generated_content(
    topic,
    content_type,
    generated_content
):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO generation_history (
            topic,
            content_type,
            generated_content
        )
        VALUES (?, ?, ?)
    """, (
        topic,
        content_type,
        generated_content
    ))

    connection.commit()

    connection.close()


# ========================================
# GET GENERATION HISTORY
# ========================================

def get_generation_history():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM generation_history
        ORDER BY created_at DESC
    """)

    history = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return history
