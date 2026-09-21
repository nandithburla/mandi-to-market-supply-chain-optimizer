from agent.tools.db import get_connection


def get_weather_summary():
    conn = get_connection()

    query = """
        SELECT
            ROUND(AVG(temperature_c), 2) AS average_temperature_c,
            ROUND(AVG(rainfall_mm), 2) AS average_rainfall_mm,
            ROUND(AVG(humidity_percent), 2) AS average_humidity_percent
        FROM weather_clean
        WHERE temperature_c IS NOT NULL
    """

    row = conn.execute(query).fetchone()
    conn.close()

    return {
        "average_temperature_c": row[0],
        "average_rainfall_mm": row[1],
        "average_humidity_percent": row[2]
    }