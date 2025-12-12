import uuid
from app.db import storage

def save_feedback(query, answer, feedback):
    storage.add_feedback({
        "id": str(uuid.uuid4()),
        "query": query,
        "answer": answer,
        "feedback": feedback,
    })

def get_negative_context():
    negs = storage.get_negative_feedbacks(limit=3)
    if not negs:
        return ""

    lines = ["Users marked these answers as unhelpful. Avoid similar responses:"]
    for i, fb in enumerate(negs, 1):
        lines.append(f"{i}. Question: {fb['query']}")
        lines.append(f"   Unhelpful answer: {fb['answer'][:200]}")
    return "\n".join(lines)
