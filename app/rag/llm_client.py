from openai import OpenAI
from app import config
from app.feedback.handler import get_negative_context

client = OpenAI(api_key=config.OPENAI_API_KEY, max_retries=2)

def generate(question, docs):
    ## Step:1 create the list/add all the context into a single list.
    lines = []                      

    for index, doc in enumerate(docs):
    # Format each document chunk as: [1] content, [2] content, ...
        line = f"[{index + 1}] {doc.page_content}"
        lines.append(line)

    # Join all lines with two newlines in between
    ctx = "\n\n".join(lines)
    fb = get_negative_context()

    system_msg = """You are a helpful assistant that answers questions based on the provided context.
- Only use information from the context to answer
- If the answer is not in the context, say "I couldn't find this information in the documents"
- Be concise and direct"""

    if fb:
        system_msg += f"\n\nLearning from user feedback:\n{fb}"

    user_msg = f"Context:\n{ctx}\n\nQuestion: {question}"

    response = client.responses.create(
        model=config.LLM_MODEL,
        instructions=system_msg,
        input=user_msg,
    )

    return response.output_text
