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

            # extract tables as markdown
            tables = page.extract_tables()
            for table in tables:
                if table:
                    md = table_to_markdown(table)
                    if md:
                        content.append(md)

            if content:
                meta = {"page": i + 1}
                if metadata:
                    meta.update(metadata)
                docs.append(Document(page_content="\n\n".join(content), metadata=meta))

    return docs

def table_to_markdown(table):
    if not table or not table[0]:
        return ""

    lines = []
    # header
    header = [str(cell or "") for cell in table[0]]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # rows
    for row in table[1:]:
        cells = [str(cell or "") for cell in row]
        # pad if needed
        while len(cells) < len(header):
            cells.append("")
        lines.append("| " + " | ".join(cells[:len(header)]) + " |")

    return "\n".join(lines)
