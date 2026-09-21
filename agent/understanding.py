import json

from agent.llm import ask_llm
from agent.prompts import SYSTEM_PROMPT


def understand_question(question):
    prompt = f"""
{SYSTEM_PROMPT}

User question:
{question}

Return only the JSON object.
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "intent": "unknown",
            "crop": None,
            "mandi": None,
        }