from agent.understanding import understand_question
from agent.tools.arrivals import get_arrivals
from agent.tools.prices import get_price_vs_msp
from agent.tools.transport import get_transport_delays
from agent.tools.weather import get_weather_summary


def run_ai_query(question):
    understanding = understand_question(question)

    intent = understanding.get("intent")
    crop = understanding.get("crop")
    mandi = understanding.get("mandi")

    if intent == "arrivals":
        data = get_arrivals(
            crop=crop,
            mandi=mandi,
            limit=10,
        )

    elif intent == "prices":
        below_msp = any(
            phrase in question.lower()
            for phrase in [
                "below msp",
                "below minimum",
                "under msp",
            ]
        )

        data = get_price_vs_msp(
            crop=crop,
            mandi=mandi,
            below_msp_only=below_msp,
            limit=10,
        )

    elif intent == "transport":
        data = get_transport_delays(
            limit=10,
        )

    elif intent == "weather":
        data = get_weather_summary()

    else:
        data = None

    return {
        "understanding": understanding,
        "data": data,
    }