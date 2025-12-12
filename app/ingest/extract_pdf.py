import pdfplumber
from langchain_core.documents import Document

def extract_pdf(path, metadata=None):
    docs = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            content = []

            # extract text
            text = page.extract_text() or ""
            if text.strip():
                content.append(text)

            # extract tables as plain text (row by row)
            for table in page.extract_tables():
                if table:
                    for row in table:
                        cells = [str(cell or "") for cell in row]
                        content.append(" | ".join(cells))

            if content:
                meta = {"page": i + 1}
                if metadata:
                    meta.update(metadata)
                docs.append(Document(page_content="\n".join(content), metadata=meta))

    return docs
