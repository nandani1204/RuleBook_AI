# Rulebook AI

AI-powered rulebook question answering and conflict detection using **Retrieval-Augmented Generation (RAG)**.

## 🚀 Overview

Rulebook AI answers questions from a rulebook corpus using semantic search and an LLM. It provides evidence for every answer and identifies whether the information is:

* ✅ **ANSWERED** — Information is available in the rulebook.
* ⚠️ **CONFLICT** — Conflicting rules are found.
* ❓ **NOT_COVERED** — The rulebook does not contain enough information.

Each response includes the **section, source, passage, and similarity score**.

## 🏗️ Architecture

```text
Rulebook Documents
       ↓
Text Extraction & Chunking
       ↓
BGE-M3 Embeddings
       ↓
ChromaDB
       ↓
Top-K Retrieval
       ↓
Gemini LLM
       ↓
ANSWERED / CONFLICT / NOT_COVERED
       ↓
FastAPI + Web UI
```

## 🛠️ Tech Stack

* Python
* FastAPI
* Google Gemini
* BAAI/bge-m3
* ChromaDB
* PyMuPDF
* HTML / CSS / JavaScript

## 📂 Project Structure

```text
rulebook_project/
├── app/
│   ├── main.py
│   ├── ingestion.py
│   ├── retrieval.py
│   └── reasoning.py
├── data/
├── frontend/
├── tests/
├── requirements.txt
└── README.md
```

▶️ How to Run
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/rulebook-ai.git
cd rulebook-ai
2. Create and activate virtual environment
python -m venv .venv

Windows:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Add Gemini API key

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key
5. Build the vector database
python -m app.ingestion
6. Start the FastAPI backend
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs
7. Start the frontend

Open a new terminal:

cd frontend
python -m http.server 5500

Open:

http://localhost:5500
🧪 Example Questions

Answered:

What is the minimum attendance requirement?

Conflict:

What is the deadline for paying semester fees?

Not Covered:

Can I pay my fees using Bitcoin?

## 🔑 Key Features

* Retrieval-Augmented Generation
* Evidence-based answers
* Conflict detection
* Hallucination prevention
* Citation and similarity scores
* Mixed-format document processing
* FastAPI 
