import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.embeddings import get_embeddings
from app import config

class VectorStore:
    def __init__(self):
        self.path = config.INDEX_PATH
        self.embeddings = get_embeddings()
        self._store = None

    @property
    def store(self):
        if not self._store:
            self._store = self._load_or_create()
        return self._store

    def _load_or_create(self):
        idx_file = os.path.join(self.path, "index.faiss")
        if os.path.exists(idx_file):
            return FAISS.load_local(self.path, self.embeddings, allow_dangerous_deserialization=True)
        # need at least one doc to init faiss
        placeholder = Document(page_content="placeholder", metadata={"_placeholder": True})
        return FAISS.from_documents([placeholder], self.embeddings)

    def add(self, docs):
        if docs:
            self.store.add_documents(docs)
            self.save()

    def search(self, query, k=None, filter=None):
        k = k or config.TOP_K
        results = self.store.similarity_search_with_score(query, k=k, filter=filter)
        # filter out placeholder
        return [(doc, score) for doc, score in results if not doc.metadata.get("_placeholder")]

    def save(self):
        os.makedirs(self.path, exist_ok=True)
        self.store.save_local(self.path)

_vs = None

def get_vector_store():
    global _vs
    if not _vs:
        _vs = VectorStore()
    return _vs
