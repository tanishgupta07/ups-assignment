import logging

from app.db import storage
from app.ingest import extract_pdf, extract_docx, chunk_docs
from app.vectorstore.faiss_store import get_vector_store

log = logging.getLogger(__name__)

EXTRACTORS = ["pdf", "docx"]

async def process_doc(doc_id: str, path: str, filename: str, ext: str, tag: str = "Public Document"):
    log.info(f"Processing: {filename} (id={doc_id}, tag={tag})")
    try:
        vs = get_vector_store()
        metadata = {"doc_id": doc_id, "file_type": ext, "tag": tag}

        # extract text based on file type
        log.info(f"Extracting text from {filename}...")
        if ext == "pdf":
            docs = extract_pdf(path, metadata=metadata)
        elif ext == "docx":
            docs = extract_docx(path, metadata=metadata)

        log.info(f"Extracted {len(docs)} document(s)")

        log.info(f"Chunking {filename}...")
        chunks = chunk_docs(docs, doc_id=doc_id)
        for c in chunks:
            c.metadata["filename"] = filename
            c.metadata["file_type"] = ext
            c.metadata["tag"] = tag
        log.info(f"Created {len(chunks)} chunks")

        log.info(f"Embedding {filename}...")
        vs.add(chunks)
        log.info(f"Embedded {len(chunks)} chunks to vector store")

        storage.add_doc({
            "id": doc_id,
            "filename": filename,
            "file_type": ext,
            "file_path": path,
            "tag": tag,
            "chunk_count": len(chunks),
            "status": "completed",
        })
        log.info(f"Done processing: {filename}")
    except Exception as e:
        log.error(f"Error processing {filename}: {e}", exc_info=True)
        storage.add_doc({
            "id": doc_id,
            "filename": filename,
            "file_type": ext,
            "file_path": path,
            "tag": tag,
            "chunk_count": 0,
            "status": "failed",
            "error": str(e),
        })
