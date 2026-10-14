# DocMind — RAG Research Assistant

DocMind is a document-grounded research assistant that allows users to upload documents, ask questions about their content, and receive AI-generated answers supported by relevant source passages.

It combines semantic search with Retrieval-Augmented Generation (RAG) to make document-based question answering more useful, accurate, and traceable.

## Features

- Upload PDF, DOCX, and TXT documents.
- Extract text from uploaded documents.
- Split extracted text into smaller, overlapping chunks.
- Generate semantic embeddings using Sentence Transformers.
- Retrieve relevant passages using FAISS similarity search.
- Generate concise, document-grounded answers using an AI model through OpenRouter.
- Display source filenames, relevance scores, and page information when available.
- Handle empty uploads, unsupported file types, and invalid questions.
- Provide a REST API using FastAPI.
- Provide an interactive dark-themed web interface using Streamlit.
- Display retrieved passages and source references alongside generated answers.

## Architecture

```text
                  Document Upload
                        |
                        v
             PDF / DOCX / TXT Extraction
                        |
                        v
                  Text Chunking
                        |
                        v
             Sentence Transformer
                   Embeddings
                        |
                        v
                  FAISS Index
                        |
                        v
                  User Question
                        |
                        v
                Semantic Search
                        |
                        v
             Relevant Passage Retrieval
                        |
                        v
             AI Answer Generation
                  (OpenRouter)
                        |
                        v
              Answer + Source References
                        |
                        v
               Streamlit Web Interface
```

## Tech Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| Development server | Uvicorn |
| Frontend interface | Streamlit |
| PDF text extraction | PyMuPDF |
| Word document extraction | python-docx |
| Text embeddings | Sentence Transformers |
| Vector similarity search | FAISS |
| Numerical processing | NumPy |
| AI answer generation | OpenRouter API |
| API client | OpenAI Python SDK |
| Environment configuration | python-dotenv |
| Testing | Python test scripts |

## Project Structure

```text
DocMind/
├── app/
│   ├── main.py
│   ├── chunker.py
│   ├── semantic_search.py
│   ├── generator.py
│   ├── ui.py
│   ├── test_chunker.py
│   ├── test_semantic_search.py
│   └── test_generator.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

**Note:** The `.env` file contains local configuration and must not be committed to GitHub.

## Getting Started

### 1. Prerequisites

- Python 3.12
- Git, for cloning and version control
- An OpenRouter API key for AI-generated answers
- Internet access for API requests and initial model downloads

### 2. Clone the Repository

After pushing the project to GitHub, replace the placeholder below with the actual repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DocMind
```

If the project is already available locally, open its root folder in the terminal instead.

### 3. Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

PyTorch and Sentence Transformers may require additional setup on some Windows systems. The Sentence Transformer model is downloaded when needed for the first time.

### 5. Configure Environment Variables

Create a `.env` file in the project root and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Replace the placeholder with your own API key.

**Security:** Never commit your actual API key or upload the `.env` file to a public repository.

### 6. Start the FastAPI Backend

From the project root, with the virtual environment activated, run:

```powershell
python -m uvicorn app.main:app --reload
```

The backend will be available at:

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

Keep this terminal running while using the application.

### 7. Start the Streamlit Frontend

Open a **second terminal** in the project root, activate the virtual environment, and run:

```powershell
.venv\Scripts\Activate.ps1
python -m streamlit run app/ui.py
```

The web interface will be available at:

http://localhost:8501

Keep both the FastAPI backend and Streamlit frontend running while using DocMind.

## API Endpoints

### `GET /`

Returns a welcome message from the DocMind API.

### `POST /upload`

Uploads and processes a supported document.

**Supported formats:** PDF, DOCX, and TXT.

The endpoint extracts text, divides it into chunks, and prepares those chunks for semantic retrieval.

### `POST /ask`

Accepts a question, retrieves relevant document passages, and uses an AI model to generate a document-grounded answer.

Example request:

```json
{
  "question": "What is DocMind?",
  "top_k": 3
}
```

The response contains:

- The submitted question
- The generated answer
- Source filenames and page references when available
- Relevance scores
- Retrieved passages used as context for answer generation

The `top_k` parameter controls the maximum number of passages retrieved for a question, subject to the API's configured validation.

## How It Works

1. **Document ingestion:** The user uploads a PDF, DOCX, or TXT file through the application.
2. **Text extraction:** The backend extracts readable text from the document.
3. **Chunking:** The extracted text is divided into smaller, overlapping passages.
4. **Embedding generation:** Sentence Transformers converts the passages into numerical vectors representing their semantic meaning.
5. **Semantic retrieval:** FAISS performs similarity search to identify passages relevant to the user's question.
6. **Answer generation:** The retrieved passages and question are sent to an AI model through OpenRouter.
7. **Source attribution:** The response includes supporting source references and relevance scores.
8. **Presentation:** The Streamlit interface displays the answer, sources, and retrieved passages.

## Testing

The project includes test scripts for text chunking, semantic search, and AI answer generation.

Run the following commands from the project root with the virtual environment activated:

### Test text chunking

```powershell
python -m app.test_chunker
```

### Test semantic search

```powershell
python -m app.test_semantic_search
```

### Test answer generation

```powershell
python -m app.test_generator
```

The answer-generation test requires a valid OpenRouter API key and a working API service.

The API has also been manually tested for:

- Successful document uploads and question answering
- Empty questions
- Questions submitted before uploading a document
- Unsupported file formats
- Empty supported files
- Questions whose answers are not present in the uploaded document

## Current Limitations

- Uploaded document chunks are stored in memory and are cleared when the backend restarts.
- The current implementation does not provide persistent document or vector storage.
- PDF page references are available, while DOCX and TXT page references are returned as `null`.
- Text extraction may not fully represent charts, images, tables, or complex document layouts.
- Answer generation depends on the availability and limits of the configured external AI service.
- The current application does not include multi-user authentication or document isolation.
- Retrieval relevance and answer quality may vary depending on the document structure, question, and retrieved passages.

## Future Improvements

- Add persistent document storage and vector indexing.
- Improve retrieval evaluation and answer-quality testing.
- Add document management and deletion features.
- Introduce multi-user authentication and access controls.
- Improve source attribution and document-level filtering.
- Explore advanced retrieval methods for tables, images, and complex document layouts.
- Add automated integration tests for the complete upload-to-answer workflow.

## Security

- Store API credentials in environment variables.
- Keep `.env` and `.venv/` out of version control.
- Never expose API keys in source code, screenshots, or public repositories.
- Validate uploaded file types and handle invalid requests safely.

## License

No license has been selected for this project yet. All rights reserved by default unless a license is added.
