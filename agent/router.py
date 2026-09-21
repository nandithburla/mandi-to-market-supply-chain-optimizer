from agent.tools.arrivals import get_arrivals
from agent.tools.prices import get_price_vs_msp
from agent.tools.transport import get_transport_delays
from agent.tools.weather import get_weather_summary


CROPS = [
    "wheat",
    "mustard",
    "maize",
    "sugarcane",
    "cotton",
    "rice",
    "narma",
    "makki",
    "kanak",
    "चावल",
    "basmati",
    "dhaan",
]

MANDIS = [
    "Hyderabad Mandi",
    "Kochi Mandi",
    "Jorhat Grain Market",
    "Baranagar Market",
    "Bathinda Grain Market",
    "Chandigarh APMC",
    "Ludhiana Grain Market",
    "Machilipatnam Mandi",
    "Aurangabad Market",
    "Orai Market",
    "Gulbarga Market",
    "Chapra Grain Market",
    "Khandwa Grain Market",
    "Panihati Market",
    "Jaunpur Mandi",
    "Jamshedpur APMC",
    "Nashik Mandi",
    "Gurgaon Grain Market",
    "Bhilwara Grain Market",
    "Dehri Mandi",
    "Kadapa Mandi",
    "Guntakal Mandi",
    "Tadipatri Mandi",
    "Gorakhpur APMC",
    "Kulti APMC",
    "Machilipatnam APMC",
    "Dhule APMC",
    "Nangloi Jat Mandi",
    "Kochi APMC",
    "Parbhani Market",
    "Dindigul APMC",
    "Bilaspur Mandi",
    "Gaya Grain Market",
    "South Dumdum Grain Market",
    "Nangloi Jat Grain Market",
    "Erode Mandi",
    "Jalandhar Mandi",
    "Patiala APMC",
    "Farrukhabad Mandi",
    "Solapur Mandi",
    "Jodhpur Market",
    "Mysore Grain Market",
    "Eluru APMC",
    "Vijayawada Mandi",
    "Chittoor Mandi",
    "Jodhpur Market",
    "Durg Market",
    "Arrah Mandi",
    "Panihati APMC",
    "Karimnagar Grain Market",
    "Guna Mandi",
    "Bijapur Market",
    "Danapur Mandi",
    "Amravati Grain Market",
    "Asansol Grain Market",
    "Kakinada APMC",
    "Anand Grain Market",
]


def route_query(query):
    q = query.lower()

    if any(
        word in q
        for word in ["arrival", "arrivals", "supply", "quantity"]
    ):
        return "arrivals"

    if any(
        word in q
        for word in [
            "msp",
            "minimum support",
            "support price",
            "price",
        ]
    ):
        return "prices"

    if any(
        word in q
        for word in [
            "transport",
            "transit",
            "warehouse",
            "delivery",
            "delay",
        ]
    ):
        return "transport"

    if any(
        word in q
        for word in [
            "weather",
            "temperature",
            "rainfall",
            "rain",
            "humidity",
        ]
    ):
        return "weather"

    return "unknown"


def extract_crop(query):
    q = query.lower()

    for crop in CROPS:
        if crop.lower() in q:
            return crop

    return None


def extract_mandi(query):
    q = query.lower()

    for mandi in MANDIS:
        if mandi.lower() in q:
            return mandi

    return None


def execute_query(query):
    intent = route_query(query)
    crop = extract_crop(query)
    mandi = extract_mandi(query)

    if intent == "arrivals":
        return intent, get_arrivals(
            crop=crop,
            mandi=mandi,
            limit=10,
        )

    if intent == "prices":
        below_msp = any(
            word in query.lower()
            for word in [
                "below msp",
                "below minimum",
                "under msp",
            ]
        )

        return intent, get_price_vs_msp(
            crop=crop,
            mandi=mandi,
            below_msp_only=below_msp,
            limit=10,
        )

    if intent == "transport":
        return intent, get_transport_delays(
            limit=10,
        )

    if intent == "weather":
        return intent, get_weather_summary()

    return intent, None