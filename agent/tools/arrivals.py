from agent.tools.db import get_connection


def get_arrivals(crop=None, mandi=None, limit=20):
    conn = get_connection()

    query = """
        SELECT
            m.mandi_name,
            a.crop,
            ROUND(SUM(a.quantity_quintal), 2) AS total_arrivals
        FROM arrivals_clean a
        JOIN mandis m ON a.mandi_id = m.mandi_id
        WHERE 1=1
    """

    params = []

    if crop:
        query += " AND LOWER(a.crop) = LOWER(?)"
        params.append(crop)

    if mandi:
        query += " AND LOWER(m.mandi_name) = LOWER(?)"
        params.append(mandi)

    query += """
        GROUP BY m.mandi_name, a.crop
        ORDER BY total_arrivals DESC
        LIMIT ?
    """

    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        {
            "mandi": row[0],
            "crop": row[1],
            "total_arrivals_quintal": row[2]
        }
        for row in rows
    ]