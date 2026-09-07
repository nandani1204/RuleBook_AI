from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.reasoning import ask_question

# --------------------------------
# Create FastAPI application
# --------------------------------

app = FastAPI(
    title="Rulebook AI",
    description="AI-powered rulebook question answering and conflict detection system",
    version="1.0.0"
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# Request model
# --------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------
# Health check
# --------------------------------

@app.get("/")
def root():
    return {
        "message": "Rulebook AI API is running",
        "status": "healthy"
    }


# --------------------------------
# Ask endpoint
# --------------------------------

@app.post("/ask")
def ask(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = ask_question(question)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )