from pathlib import Path
import re

import chromadb
import pymupdf
from sentence_transformers import SentenceTransformer


# -----------------------------
# Configuration
# -----------------------------

DATA_DIR = Path("data")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "rulebook"

# Multilingual model works well for English + Hinglish queries
EMBEDDING_MODEL = "BAAI/bge-m3"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


# -----------------------------
# Initialize embedding model
# -----------------------------

print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


# -----------------------------
# Initialize ChromaDB
# -----------------------------

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# -----------------------------
# Read files
# -----------------------------

def read_markdown_file(file_path: Path) -> str:
    """Read a markdown/text file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_pdf_file(file_path: Path) -> str:
    """Extract text from a PDF."""

    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text() + "\n"

    document.close()

    return text


def read_file(file_path: Path) -> str:
    """Read supported file types."""

    extension = file_path.suffix.lower()

    if extension in [".md", ".txt"]:
        return read_markdown_file(file_path)

    elif extension == ".pdf":
        return read_pdf_file(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


# -----------------------------
# Extract sections
# -----------------------------

def extract_sections(text: str):
    """
    Split rulebook text using markdown headings.

    Example:

    ## 2.1 General Attendance Requirement

    becomes:

    section = 2.1
    title = General Attendance Requirement
    """

    pattern = r"(?m)^#{1,3}\s+(.+)$"

    matches = list(re.finditer(pattern, text))

    sections = []

    for i, match in enumerate(matches):

        title = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        # Try to extract section number such as 2.1, 6.2, 7.5
        section_match = re.match(
            r"(\d+(?:\.\d+)*)\s*(.*)",
            title
        )

        if section_match:
            section_number = section_match.group(1)
            clean_title = section_match.group(2).strip()
        else:
            section_number = "unknown"
            clean_title = title

        if section_text:
            sections.append({
                "section": section_number,
                "title": clean_title,
                "text": section_text
            })

    return sections


# -----------------------------
# Chunk text
# -----------------------------

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split long sections into overlapping chunks.

    Character-based chunking is enough for this project
    and keeps the implementation easy to understand.
    """

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


# -----------------------------
# Process one document
# -----------------------------

def process_document(file_path: Path):
    """Read and convert one document into chunks."""

    print(f"Processing: {file_path.name}")

    text = read_file(file_path)

    if not text.strip():
        print("  Empty document. Skipping.")
        return []

    sections = extract_sections(text)

    documents = []

    for section in sections:

        chunks = chunk_text(section["text"])

        for chunk_index, chunk in enumerate(chunks):

            documents.append({
                "text": chunk,

                "metadata": {
                    "section": section["section"],
                    "title": section["title"],
                    "source": file_path.name,
                    "chunk_index": chunk_index
                }
            })

    print(
        f"  Sections: {len(sections)} | "
        f"Chunks: {len(documents)}"
    )

    return documents


# -----------------------------
# Store documents in ChromaDB
# -----------------------------

def store_documents(documents):
    """Generate embeddings and store chunks in ChromaDB."""

    if not documents:
        return

    texts = [
        document["text"]
        for document in documents
    ]

    metadatas = [
        document["metadata"]
        for document in documents
    ]

    # Generate embeddings
    print("Generating embeddings...")

    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    # Create unique IDs
    ids = [
        f"{metadata['source']}_{metadata['section']}_{metadata['chunk_index']}_{i}"
        for i, metadata in enumerate(metadatas)
    ]

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Stored {len(documents)} chunks.")


# -----------------------------
# Main ingestion pipeline
# -----------------------------

def ingest():

    if not DATA_DIR.exists():
        print("Data directory does not exist.")
        return

    all_documents = []

    supported_extensions = [
        ".md",
        ".txt",
        ".pdf"
    ]

    files = [
        file
        for file in DATA_DIR.iterdir()
        if file.suffix.lower() in supported_extensions
    ]

    if not files:
        print("No supported documents found.")
        return

    print(f"Found {len(files)} documents.\n")

    for file_path in files:

        documents = process_document(file_path)

        all_documents.extend(documents)

    print(
        f"\nTotal chunks generated: "
        f"{len(all_documents)}"
    )

    store_documents(all_documents)

    print("\nIngestion completed successfully!")
    print(f"ChromaDB location: {CHROMA_DIR}")


# -----------------------------
# Run script
# -----------------------------

if __name__ == "__main__":
    ingest()