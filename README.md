# Document Q&A

A RAG chatbot that answers questions from your PDF and DOCX files.

## What it does

- Upload PDF/DOCX documents
- Ask questions about them
- Get answers with sources
- Chat sessions persist so you can pick up where you left off

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI key
OPENAI_API_KEY=your-key-here
```

## Running

Start the backend:
```bash
uvicorn app.main:app --reload
```

Start the frontend (in another terminal):
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Project structure

```
app/
  main.py          # API endpoints
  config.py        # Settings
  db/storage.py    # JSON file storage for docs, sessions, feedback
  ingest/          # PDF/DOCX extraction and chunking
  rag/             # Query pipeline and LLM calls
  vectorstore/     # FAISS index

frontend/          # React app

data/
  sessions/        # Chat sessions (UUID.json files)
  metadata.json    # Uploaded document info
  feedback.json    # User feedback
  faiss_index/     # Vector embeddings
```

## Config

Set these in `.env` or `app/config.py`:

- `OPENAI_API_KEY` - Your OpenAI API key
- `LLM_MODEL` - Model to use (default: gpt-3.5-turbo)
- `CHUNK_SIZE` - Text chunk size (default: 1000)
- `TOP_K` - Number of results to retrieve (default: 5)
