from langchain_community.document_loaders import Docx2txtLoader

def extract_docx(path, metadata=None):
    loader = Docx2txtLoader(path)
    docs = loader.load()

    # add custom metadata
    if metadata:
        for doc in docs:
            doc.metadata.update(metadata)

    return docs
