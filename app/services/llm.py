from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful enterprise IT support assistant.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
