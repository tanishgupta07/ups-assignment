from app.vectorstore.faiss_store import get_vector_store

def retrieve(query, k=None, filter=None):
    vs = get_vector_store()
    return vs.search(query, k=k, filter=filter)
