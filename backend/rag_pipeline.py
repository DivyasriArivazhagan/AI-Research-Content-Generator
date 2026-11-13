
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer


# Load embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(
    path="vector_db"
)

collection = chroma_client.get_or_create_collection(
    name="research_documents"
)


# STEP 1: Text Chunking
def split_text(text, chunk_size=1000, chunk_overlap=200):

    if not text or not text.strip():
        return []

    if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - chunk_overlap

    return chunks


# STEP 2: Generate Embeddings
def create_embeddings(chunks):

    if not chunks:
        return []

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings


# STEP 3: Generate Document Hash
def generate_document_hash(chunks):

    document_content = "\n".join(chunks)

    return hashlib.sha256(
        document_content.encode("utf-8")
    ).hexdigest()


# STEP 4: Check Duplicate Documents
def is_duplicate_document(chunks, document_hash):

    if collection.count() == 0:
        return False

    # Check documents uploaded using the new hash system
    hash_results = collection.get(
        where={"document_hash": document_hash},
        include=["metadatas"]
    )

    if hash_results.get("ids"):
        return True

    # Check older documents that do not have document_hash metadata
    # This also detects duplicates from earlier uploads.
    existing = collection.get(
        include=["documents", "metadatas"]
    )

    existing_documents = {}

    for document, metadata in zip(
        existing.get("documents", []),
        existing.get("metadatas", [])
    ):

        source = metadata.get("source", "unknown")
        chunk_number = metadata.get("chunk_number", 0)

        if source not in existing_documents:
            existing_documents[source] = []

        existing_documents[source].append(
            (chunk_number, document)
        )

    new_content = tuple(chunks)

    for source, stored_chunks in existing_documents.items():

        stored_chunks.sort(key=lambda item: item[0])

        old_content = tuple(
            chunk for _, chunk in stored_chunks
        )

        if old_content == new_content:
            return True

    return False


# STEP 5: Store Chunks in ChromaDB
def store_chunks(chunks, source):

    if not chunks:
        return 0

    document_hash = generate_document_hash(chunks)

    if is_duplicate_document(chunks, document_hash):

        print(f"Duplicate document detected: {source}")
        return 0

    embeddings = create_embeddings(chunks)

    ids = [
        hashlib.sha256(
            f"{document_hash}_{i}".encode("utf-8")
        ).hexdigest()
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": source,
            "chunk_number": i + 1,
            "document_hash": document_hash
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(f"Successfully stored {len(chunks)} chunks.")

    return len(chunks)


# STEP 6: Retrieve Relevant Chunks
def retrieve_relevant_chunks(query, n_results=5):

    if not query or not query.strip():
        return []

    if collection.count() == 0:
        return []

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):

        retrieved_chunks.append({
            "text": document,
            "source": metadata["source"],
            "chunk_number": metadata["chunk_number"],
            "distance": distance
        })

    return retrieved_chunks
