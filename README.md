# IIUM Policy Assistant

An AI-powered assistant that uses Retrieval-Augmented Generation (RAG) to answer questions about International Islamic University Malaysia (IIUM) policies and regulations using relevant document evidence.

## Features

- Retrieves relevant policy information from IIUM documents.
- Uses semantic search, reranking, and metadata-aware filtering.
- Generates evidence-based answers using Groq.
- Returns source document and page information.
- Stores search history in Supabase.
- Provides a FastAPI backend with interactive API documentation.

## Technology Stack

- Python
- FastAPI
- Sentence Transformers
- FAISS
- Groq API
- Supabase
- PyMuPDF

## Project Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd iium-policy-assistant
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add the required credentials:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SECRET_KEY=your_supabase_secret_key
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
```

Replace the example values with your own credentials. Never commit `.env` to GitHub.

### 5. Add policy documents

Place authorized IIUM policy PDF documents in:

```text
data/documents/
```

### 6. Build the vector store

Follow the project's vector-store build procedure to process the PDF documents and generate the FAISS index and metadata.

### 7. Start the API

From the project root, run:

```powershell
uvicorn backend.main:app --reload
```

Open the interactive API documentation at:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check API status |
| POST | `/search` | Retrieve relevant policy evidence |
| POST | `/ask` | Generate an answer from retrieved evidence |
| GET | `/history` | Retrieve saved search history |
| GET | `/history/{history_id}` | Retrieve a specific history record |

For POST endpoints, submit a JSON body such as:

```json
{
  "query": "What are the tuition fees for Malaysian undergraduate students?"
}
```

## Security Note

API credentials and private configuration files must remain outside version control. Authentication, user-specific history access, and production deployment settings should be reviewed before exposing the API publicly.

## Project Status

Developed as a Final Year Project at the International Islamic University Malaysia (IIUM).