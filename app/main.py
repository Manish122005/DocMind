from io import BytesIO
from pathlib import Path
from app.generator import generate_answer
import pymupdf
from docx import Document
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.chunker import chunk_text
from app.semantic_search import search_chunks

app = FastAPI(title="DocMind API")

# Temporary storage: cleared when the server restarts.
document_chunks = []


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


@app.get("/")
def home():
    return {"message": "Welcome to DocMind!"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400, detail="Only PDF, DOCX, and TXT files are supported."
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="File is empty.")

    try:
        pages = []

        if extension == ".pdf":
            with pymupdf.open(stream=content, filetype="pdf") as pdf:
                pages = [
                    {"page": i + 1, "text": page.get_text()}
                    for i, page in enumerate(pdf)
                ]

        elif extension == ".docx":
            doc = Document(BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            pages = [{"page": None, "text": text}]

        else:
            text = content.decode("utf-8-sig")
            pages = [{"page": None, "text": text}]

    except Exception as exc:
        raise HTTPException(
            status_code=400, detail="Could not read this document."
        ) from exc

    new_chunks = []

    for page_data in pages:
        text = page_data["text"]

        for chunk in chunk_text(text):
            new_chunks.append(
                {"text": chunk, "filename": filename, "page": page_data["page"]}
            )

    if not new_chunks:
        raise HTTPException(
            status_code=400, detail="No readable text found in the document."
        )

    # Replace earlier chunks for a file with the same filename.
    document_chunks[:] = [
        item for item in document_chunks if item["filename"] != filename
    ]
    document_chunks.extend(new_chunks)

    return {
        "filename": filename,
        "chunks_created": len(new_chunks),
        "message": "Document processed and indexed for retrieval.",
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not document_chunks:
        raise HTTPException(
            status_code=400, detail="Upload a document before asking a question."
        )

    if not 1 <= request.top_k <= 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10.")

    texts = [item["text"] for item in document_chunks]

    matches = search_chunks(texts, request.question, top_k=request.top_k)

    results = []

    for match in matches:
        source = document_chunks[match["index"]]

        results.append(
            {
                "text": match["text"],
                "score": round(match["score"], 3),
                "source": source["filename"],
                "page": source["page"],
            }
        )

    if not results:
        raise HTTPException(status_code=404, detail="No relevant passages were found.")

    try:
        answer = generate_answer(request.question, results)

    except Exception as exc:
        print(f"AI generation failed: {type(exc).__name__}: {exc}")

        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable. Please try again later.",
        ) from exc

    return {
        "question": request.question,
        "answer": answer,
        "sources": [
            {"source": item["source"], "page": item["page"], "score": item["score"]}
            for item in results
        ],
        "retrieved_passages": results,
    }
