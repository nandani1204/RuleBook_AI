import os
import json

from dotenv import load_dotenv
from google import genai

from app.retrieval import retrieve_documents


# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )


# -----------------------------
# Gemini client
# -----------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.7-flash"

# -----------------------------
# Build context
# -----------------------------

def build_context(documents):

    context = ""

    for i, document in enumerate(documents, 1):

        context += f"""
PASSAGE {i}

Section: {document['section']}
Title: {document['title']}
Source: {document['source']}
Similarity: {document['similarity']}

Text:
{document['text']}

-----------------------------
"""

    return context


# -----------------------------
# Reason over retrieved evidence
# -----------------------------

def analyze_question(question, documents):

    if not documents:
        return {
            "status": "NOT_COVERED",
            "answer": "The rulebook does not contain enough information to answer this question.",
            "sources": []
        }

    context = build_context(documents)

    prompt = f"""
You are a strict university rulebook question-answering
and consistency-analysis system.

You MUST answer using ONLY the supplied rulebook passages.

Do NOT use outside knowledge.
Do NOT invent rules.
Do NOT assume information that is not explicitly present.

The system has exactly three possible statuses:

1. ANSWERED
Use ANSWERED when the retrieved passages provide
sufficient information to answer the question.

2. NOT_COVERED
Use NOT_COVERED when the rulebook passages do not
provide enough information to answer the question.

3. CONFLICT
Use CONFLICT when two or more passages explicitly
give incompatible rules or requirements for the same
situation.

Important:
A general rule and a clearly stated exception are NOT
automatically a conflict.

For example:
"75% attendance is required generally"
and
"students with approved medical exemption may appear
with at least 60%"
can be an exception rather than a conflict.

For CONFLICT:
- Explain the disagreement.
- Show both rules.
- Mention their sections.

For ANSWERED:
- Give a concise answer.
- Cite the relevant section(s).

For NOT_COVERED:
- Clearly state that the rulebook does not specify
  the requested situation.
- Do not make up an answer.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "status": "ANSWERED | NOT_COVERED | CONFLICT",
    "answer": "your answer",
    "sections": ["section numbers"],
    "reason": "short explanation"
}}

USER QUESTION:
{question}

RETRIEVED RULEBOOK PASSAGES:

{context}
"""

    response = client.models.generate_content(
    model=MODEL_NAME,
    contents=prompt
    )
    raw_response = response.text.strip()
    # Remove markdown code fences if Gemini adds them
    if raw_response.startswith("```"):
        raw_response = raw_response.replace(
            "```json", ""
        ).replace("```", "").strip()

    try:
        result = json.loads(raw_response)

    except json.JSONDecodeError:

        return {
            "status": "ERROR",
            "answer": "The AI returned an invalid response.",
            "sections": [],
            "reason": raw_response
        }

    return result


# -----------------------------
# Complete RAG pipeline
# -----------------------------

def ask_question(question):

    documents = retrieve_documents(
        question,
        top_k=5
    )

    result = analyze_question(
        question,
        documents
    )

    # Attach retrieved evidence
    result["sources"] = documents

    return result


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    question = input(
        "\nAsk a rulebook question: "
    )

    result = ask_question(question)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )