import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Configuration
# -----------------------------

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "rulebook"

EMBEDDING_MODEL = "BAAI/bge-m3"

TOP_K = 5
SIMILARITY_THRESHOLD = 0.1


# -----------------------------
# Initialize model
# -----------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# -----------------------------
# Initialize ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# -----------------------------
# Retrieve relevant documents
# -----------------------------

def retrieve_documents(
    query: str,
    top_k: int = TOP_K,
    threshold: float = SIMILARITY_THRESHOLD
    ):
    """
    Search ChromaDB for the most relevant
    rulebook passages.
    """

    if not query or not query.strip():
        return []

    # Convert user question into embedding
    query_embedding = embedding_model.encode(
        query
    ).tolist()

    # Search vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_documents = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Chroma returns distance.
        # For cosine distance:
        # similarity = 1 - distance
        similarity = 1 - distance
        if similarity < threshold:
            continue

        retrieved_documents.append({
            "text": document,
            "section": metadata.get("section", "Unknown"),
            "title": metadata.get("title", "Unknown"),
            "source": metadata.get("source", "Unknown"),
            "chunk_index": metadata.get(
                "chunk_index",
                0
            ),
            "similarity": round(
                similarity,
                4
            )
        })

    return retrieved_documents


# -----------------------------
# Test retrieval
# -----------------------------

if __name__ == "__main__":

    question = input(
        "\nEnter your question: "
    )

    results = retrieve_documents(question)

    print("\n" + "=" * 60)
    print("RETRIEVED PASSAGES")
    print("=" * 60)

    for i, result in enumerate(results, 1):

        print(f"\nResult {i}")
        print("-" * 40)

        print(
            f"Section: {result['section']}"
        )

        print(
            f"Title: {result['title']}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Similarity: {result['similarity']}"
        )

        print(
            f"\nPassage:\n{result['text']}"
        )