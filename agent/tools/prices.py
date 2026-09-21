from agent.tools.db import get_connection


def get_price_vs_msp(crop=None, mandi=None, below_msp_only=False, limit=20):
    conn = get_connection()

    query = """
        SELECT
            m.mandi_name,
            p.crop,
            ROUND(AVG(p.modal_price), 2) AS avg_price,
            ROUND(AVG(p.msp_per_quintal), 2) AS avg_msp,
            ROUND(AVG(p.msp_gap), 2) AS avg_gap,
            SUM(p.below_msp) AS below_msp_count,
            COUNT(*) AS total_records
        FROM prices_clean p
        JOIN mandis m ON p.mandi_id = m.mandi_id
        WHERE p.modal_price IS NOT NULL
          AND p.msp_per_quintal IS NOT NULL
    """

    params = []

    if crop:
        query += " AND LOWER(p.crop) = LOWER(?)"
        params.append(crop)

    if mandi:
        query += " AND LOWER(m.mandi_name) = LOWER(?)"
        params.append(mandi)

    query += """
        GROUP BY m.mandi_name, p.crop
    """

    if below_msp_only:
        query += " HAVING AVG(p.msp_gap) < 0"

    query += """
        ORDER BY avg_gap ASC
        LIMIT ?
    """

    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        {
            "mandi": row[0],
            "crop": row[1],
            "average_price": row[2],
            "average_msp": row[3],
            "average_gap": row[4],
            "below_msp_count": row[5],
            "total_records": row[6]
        }
        for row in rows
    ]