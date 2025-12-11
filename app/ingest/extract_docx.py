from docx import Document as DocxDocument
from langchain_core.documents import Document

def extract_docx(path, metadata=None):
    doc = DocxDocument(path)
    content = []

    for element in doc.element.body:
        tag = element.tag.split('}')[-1]

        if tag == 'p':
            # paragraph
            para = element.text
            if para and para.strip():
                content.append(para)

        elif tag == 'tbl':
            # table - find it in doc.tables
            for table in doc.tables:
                if table._tbl == element:
                    md = table_to_markdown(table)
                    if md:
                        content.append(md)
                    break

    meta = metadata or {}
    return [Document(page_content="\n\n".join(content), metadata=meta)]

def table_to_markdown(table):
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)

    if not rows:
        return ""

    lines = []
    # header
    header = rows[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # data rows
    for row in rows[1:]:
        # pad if needed
        while len(row) < len(header):
            row.append("")
        lines.append("| " + " | ".join(row[:len(header)]) + " |")

    return "\n".join(lines)
