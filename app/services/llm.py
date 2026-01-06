import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an internal enterprise knowledge assistant.
Answer ONLY using the provided context.
If the answer is not found in the context, say:
"Information not available in the knowledge base."
"""

def generate_answer(question: str, context_chunks: list):
    context_text = "\n\n".join(
        f"- {chunk['text']}" for chunk in context_chunks
    )

    prompt = f"""
Context:
{context_text}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
