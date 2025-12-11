from openai import OpenAI
from app import config
from app.feedback.handler import get_negative_context

client = OpenAI(api_key=config.OPENAI_API_KEY, max_retries=2)

def generate(question, docs):
    ctx = "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(docs)])
    fb = get_negative_context()

    system_msg = "Answer based on the context below. If you can't find the answer, say so."
    if fb:
        system_msg += f"\n\n{fb}"

    user_msg = f"Context:\n{ctx}\n\nQuestion: {question}"

    response = client.responses.create(
        model=config.LLM_MODEL,
        instructions=system_msg,
        input=user_msg,
    )

    return response.output_text
