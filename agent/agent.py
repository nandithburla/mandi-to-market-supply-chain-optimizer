import os
import json
from agent.ai_router import run_ai_query
from agent.final_answer import generate_final_answer
from agent.charts import create_chart
from agent.llm import get_api_key
from agent.router import execute_query
from agent.response import format_response


def ask_agent(query):
    api_key = get_api_key()
    
    # If OpenRouter API key is available, execute full LLM pipeline
    if api_key:
        try:
            result = run_ai_query(query)
            understanding = result["understanding"]
            data = result["data"]
            intent = understanding.get("intent")

            if intent == "unknown":
                return {
                    "answer": (
                        "I can answer questions about mandi arrivals, "
                        "crop prices, MSP, transport, warehouses, and weather "
                        "from the available agricultural dataset."
                    ),
                    "intent": "unknown",
                    "data": None,
                    "chart": None,
                }

            answer = generate_final_answer(
                query,
                understanding,
                data,
            )

            fig = create_chart(intent, data)
            chart_dict = json.loads(fig.to_json()) if fig is not None and hasattr(fig, "to_json") else None

            return {
                "answer": answer,
                "intent": intent,
                "data": data,
                "chart": chart_dict,
            }
        except Exception:
            # Fall back to deterministic query routing if LLM call fails
            pass

    # Deterministic fallback when API key is not configured or network error occurs
    intent, data = execute_query(query)
    answer = format_response(intent, data)
    fig = create_chart(intent, data)
    chart_dict = json.loads(fig.to_json()) if fig is not None and hasattr(fig, "to_json") else None

    return {
        "answer": answer,
        "intent": intent,
        "data": data,
        "chart": chart_dict,
    }