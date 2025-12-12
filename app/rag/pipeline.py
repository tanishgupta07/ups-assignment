import logging
from app.retriever.retriever import retrieve
from app.rag.llm_client import generate

log = logging.getLogger(__name__)

def query(question, chat_history=None, k=None, filter=None):
    log.info(f"Query: {question}")

    # get relevant docs
    log.info("Retrieving documents...")
    results = retrieve(question, k=k, filter=filter)
    docs = [doc for doc, _ in results]
    log.info(f"Retrieved {len(docs)} documents")

    # generate answer
    log.info("Generating answer...")
    answer = generate(question, docs)
    log.info("Answer generated")

    # format sources
    sources = []
    for doc, score in results:
        sources.append({
            "content": doc.page_content[:500],
            "metadata": doc.metadata,
            "score": float(score),
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }
