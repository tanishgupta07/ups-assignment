import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app import config

def chunk_docs(docs, doc_id=None):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_idx"] = i

    # Save debug file
    if doc_id:
        _save_chunks_debug(chunks, doc_id)

    return chunks

def _save_chunks_debug(chunks, doc_id):
    debug_dir = os.path.join(config.DATA_DIR, "chunks_debug")
    os.makedirs(debug_dir, exist_ok=True)
    debug_file = os.path.join(debug_dir, f"{doc_id}_chunks.txt")

    with open(debug_file, "w") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"{'='*60}\n")
            f.write(f"Chunk {i + 1}:\n")
            f.write(f"Metadata: {chunk.metadata}\n")
            f.write(f"{'='*60}\n")
            f.write(chunk.page_content)
            f.write(f"\n\n")
