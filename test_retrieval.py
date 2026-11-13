
from backend.rag_pipeline import retrieve_relevant_chunks

# User search topic
topic = input("Enter your research topic: ")

# Retrieve relevant information
results = retrieve_relevant_chunks(topic, n_results=5)

print("\nRelevant Information Found:")
print("--------------------------------")

if not results:
    print("No relevant information found.")

else:
    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("Source:", result["source"])
        print("Chunk Number:", result["chunk_number"])
        print("Content:")
        print(result["text"])
