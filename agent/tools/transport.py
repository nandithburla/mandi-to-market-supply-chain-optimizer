from agent.tools.db import get_connection


def get_transport_delays(warehouse=None, limit=10):
    conn = get_connection()

    query = """
        SELECT
            destination_warehouse,
            ROUND(AVG(transit_hours_clean), 2) AS average_transit_hours,
            COUNT(*) AS total_trips
        FROM transport_clean
        WHERE transit_time_invalid = 0
          AND transit_hours_clean IS NOT NULL
    """

    params = []

    if warehouse:
        query += " AND LOWER(destination_warehouse) = LOWER(?)"
        params.append(warehouse)

    query += """
        GROUP BY destination_warehouse
        ORDER BY average_transit_hours DESC
        LIMIT ?
    """

    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        {
            "warehouse": row[0],
            "average_transit_hours": row[1],
            "total_trips": row[2]
        }
        for row in rows
    ]