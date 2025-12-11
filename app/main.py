import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import config
from app.db import storage
from app.rag.pipeline import query
from app.feedback.handler import save_feedback
from app.ingest.process_doc import process_doc, EXTRACTORS

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="RAG App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class QueryReq(BaseModel):
    question: str
    session_id: str
    k: int | None = None
    filter: dict | None = None

class FeedbackReq(BaseModel):
    query: str
    answer: str
    feedback: str

# ---------- Root ----------

@app.get("/")
async def root():
    return {"app": "RAG", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------- Sessions ----------

@app.post("/sessions")
async def create_session():
    session = storage.create_session()
    return session

@app.get("/sessions")
async def list_sessions():
    return {"sessions": storage.get_all_sessions()}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if storage.delete_session(session_id):
        return {"ok": True}
    raise HTTPException(404, "Session not found")

# ---------- Query ----------

@app.post("/query")
async def ask(req: QueryReq):
    try:
        # get last 5 messages from session as context
        chat_history = storage.get_chat_history(req.session_id, limit=5)

        result = query(
            question=req.question,
            chat_history=chat_history,
            k=req.k,
            filter=req.filter
        )

        # save message to session (including sources)
        storage.add_message(req.session_id, req.question, result["answer"], result["sources"])

        return result
    except Exception as e:
        raise HTTPException(500, str(e))

# ---------- Feedback ----------

@app.post("/feedback")
async def submit_feedback(req: FeedbackReq):
    save_feedback(req.query, req.answer, req.feedback)
    return {"ok": True}

# ---------- Ingest ----------

DOCUMENT_TAGS = ["Finance Document", "Business Document", "Public Document"]

@app.get("/ingest/tags")
async def get_tags():
    return {"tags": DOCUMENT_TAGS}

@app.post("/ingest/upload")
async def upload(bg: BackgroundTasks, file: UploadFile = File(...), tag: str = "Public Document", force: bool = False):
    name = file.filename
    ext = name.split(".")[-1].lower()

    if ext not in EXTRACTORS:
        raise HTTPException(400, f"Unsupported: {ext}")

    if tag not in DOCUMENT_TAGS:
        raise HTTPException(400, f"Invalid tag. Must be one of: {DOCUMENT_TAGS}")

    existing = storage.get_doc_by_name(name)

    if existing and not force:
        return {"document_id": existing["id"], "filename": name, "message": "exists"}

    if existing and force:
        storage.delete_doc(existing["id"])
        if existing.get("file_path") and os.path.exists(existing["file_path"]):
            os.remove(existing["file_path"])

    content = await file.read()
    doc_id = str(uuid.uuid4())
    path = os.path.join(config.RAW_DIR, f"{doc_id}.{ext}")
    os.makedirs(config.RAW_DIR, exist_ok=True)

    with open(path, "wb") as f:
        f.write(content)

    bg.add_task(process_doc, doc_id, path, name, ext, tag)

    return {"document_id": doc_id, "filename": name, "tag": tag, "message": "processing"}

@app.get("/ingest/documents")
async def list_docs():
    return {"documents": storage.get_all_docs()}

@app.get("/ingest/documents/{doc_id}")
async def get_doc_status(doc_id: str):
    doc = storage.get_doc(doc_id)
    if not doc:
        raise HTTPException(404)
    return doc

@app.delete("/ingest/documents/{doc_id}")
async def delete_doc(doc_id: str):
    doc = storage.get_doc(doc_id)
    if not doc:
        raise HTTPException(404)
    storage.delete_doc(doc_id)
    if doc.get("file_path") and os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
