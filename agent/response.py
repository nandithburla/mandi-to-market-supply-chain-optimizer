def format_response(intent, data):
    if intent == "weather":
        return (
            f"Average temperature is {data['average_temperature_c']}°C, "
            f"average rainfall is {data['average_rainfall_mm']} mm, "
            f"and average humidity is {data['average_humidity_percent']}%."
        )

    if not data:
        return "I could not find matching data in the dataset."

    if intent == "arrivals":
        lines = ["Here are the mandis with the highest arrivals:"]
        for i, item in enumerate(data[:5], 1):
            lines.append(
                f"{i}. {item['mandi']} — "
                f"{item['total_arrivals_quintal']:,.2f} quintals of {item['crop']}"
            )
        return "\n".join(lines)

    if intent == "prices":
        lines = ["Here are the price vs MSP results:"]
        for i, item in enumerate(data[:5], 1):
            lines.append(
                f"{i}. {item['mandi']} — "
                f"Price ₹{item['average_price']} | "
                f"MSP ₹{item['average_msp']} | "
                f"Gap ₹{item['average_gap']}"
            )
        return "\n".join(lines)

    if intent == "transport":
        lines = ["Average transport time by destination:"]
        for i, item in enumerate(data[:5], 1):
            lines.append(
                f"{i}. {item['warehouse']} — "
                f"{item['average_transit_hours']} hours "
                f"({item['total_trips']} trips)"
            )
        return "\n".join(lines)

    return "I could not understand the question."