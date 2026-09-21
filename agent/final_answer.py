import json

from agent.llm import ask_llm


def generate_final_answer(question, understanding, data):
    prompt = f"""
You are an agricultural assistant helping farmers.

Answer the user's question using ONLY the provided database results.

User question:
{question}

Question understanding:
{json.dumps(understanding, ensure_ascii=False)}

Database results:
{json.dumps(data, ensure_ascii=False)}

Rules:
- Use only the provided database results.
- Do not invent numbers or facts.
- Keep the answer simple and easy for a farmer to understand.
- Mention important numbers clearly.
- If the results contain multiple mandis, summarize the important ones.
- Do not mention SQL, Python, APIs, or internal system details.
"""

    return ask_llm(prompt)