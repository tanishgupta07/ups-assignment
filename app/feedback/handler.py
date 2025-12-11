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

    lines = ["Avoid these types of answers that users found unhelpful:"]
    for fb in negs:
        lines.append(f"Q: {fb['query']}")
        lines.append(f"Bad A: {fb['answer'][:150]}...")
    return "\n".join(lines)
