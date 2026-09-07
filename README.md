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

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Gemini API key

Create `.env`:

```env
GEMINI_API_KEY=your_api_key
```

### 3. Build the vector database

```bash
python -m app.ingestion
```

### 4. Start FastAPI

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Start frontend

```bash
cd frontend
python -m http.server 5500
```

Open:

```text
http://localhost:5500
```

## 🧪 Example Questions

**Answered:**

> What is the minimum attendance requirement?

**Conflict:**

> What is the deadline for paying semester fees?

**Not Covered:**

> Can I pay my fees using Bitcoin?

## 🔑 Key Features

* Retrieval-Augmented Generation
* Evidence-based answers
* Conflict detection
* Hallucination prevention
* Citation and similarity scores
* Mixed-format document processing
* FastAPI 
