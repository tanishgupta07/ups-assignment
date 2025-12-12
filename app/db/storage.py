import os
import json
import uuid
from datetime import datetime, timezone
from app import config

# ensure dirs and files exist
for dir_path in [config.DATA_DIR, config.RAW_DIR, config.INDEX_PATH, config.SESSIONS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

if not os.path.exists(config.METADATA_FILE):
    with open(config.METADATA_FILE, "w") as f:
        json.dump({"documents": []}, f)

if not os.path.exists(config.FEEDBACK_FILE):
    with open(config.FEEDBACK_FILE, "w") as f:
        json.dump({"feedbacks": []}, f)

# ---------- Documents ----------

def add_doc(doc):
    with open(config.METADATA_FILE) as f:
        data = json.load(f)
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    data["documents"].append(doc)
    with open(config.METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def get_doc(doc_id):
    with open(config.METADATA_FILE) as f:
        data = json.load(f)
    for d in data.get("documents", []):
        if d["id"] == doc_id:
            return d
    return None

def get_doc_by_name(filename):
    with open(config.METADATA_FILE) as f:
        data = json.load(f)
    for d in data.get("documents", []):
        if d.get("filename") == filename:
            return d
    return None

def get_all_docs():
    with open(config.METADATA_FILE) as f:
        data = json.load(f)
    return data.get("documents", [])

def delete_doc(doc_id):
    with open(config.METADATA_FILE) as f:
        data = json.load(f)
    data["documents"] = [d for d in data["documents"] if d["id"] != doc_id]
    with open(config.METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ---------- Feedback ----------

def add_feedback(fb):
    with open(config.FEEDBACK_FILE) as f:
        data = json.load(f)
    fb["created_at"] = datetime.now(timezone.utc).isoformat()
    data["feedbacks"].append(fb)
    with open(config.FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def get_negative_feedbacks(limit=3):
    with open(config.FEEDBACK_FILE) as f:
        data = json.load(f)
    negs = [f for f in data.get("feedbacks", []) if f.get("feedback") == "negative"]
    negs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return negs[:limit]

# ---------- Sessions ----------

def _session_path(session_id):
    return os.path.join(config.SESSIONS_DIR, f"{session_id}.json")

def create_session():
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": []
    }
    with open(_session_path(session_id), "w") as f:
        json.dump(session, f, indent=2)
    return session

def get_session(session_id):
    path = _session_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def add_message(session_id, question, answer, sources=None):
    session = get_session(session_id)
    if not session:
        return None
    session["messages"].append({
        "question": question,
        "answer": answer,
        "sources": sources or [],
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    with open(_session_path(session_id), "w") as f:
        json.dump(session, f, indent=2)
    return session

def get_chat_history(session_id, limit=5):
    """Get last N messages as (question, answer) tuples for context."""
    session = get_session(session_id)
    if session is None:
        return []

    # Extract only the last `limit` messages
    recent_messages = session.get("messages", [])[-limit:]

    # Convert each message into a (question, answer) tuple
    history = []
    for message in recent_messages:
        history.append((message["question"], message["answer"]))

    return history

def get_all_sessions():
    sessions = []
    for filename in os.listdir(config.SESSIONS_DIR):
        if filename.endswith(".json"):
            path = os.path.join(config.SESSIONS_DIR, filename)
            with open(path) as f:
                session = json.load(f)
                sessions.append({
                    "id": session["id"],
                    "created_at": session["created_at"],
                    "message_count": len(session.get("messages", []))
                })
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions

def delete_session(session_id):
    path = _session_path(session_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
