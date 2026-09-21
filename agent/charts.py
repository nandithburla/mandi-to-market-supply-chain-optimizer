import plotly.express as px


def create_chart(intent, data):
    if not data:
        return None

    if intent == "arrivals":
        fig = px.bar(
            data,
            x="mandi",
            y="total_arrivals_quintal",
            title="Mandi Arrivals",
            labels={
                "mandi": "Mandi",
                "total_arrivals_quintal": "Arrivals (Quintals)",
            },
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
        )

        return fig

    if intent == "prices":
        fig = px.bar(
            data,
            x="mandi",
            y=["average_price", "average_msp"],
            title="Average Price vs MSP",
            labels={
                "mandi": "Mandi",
                "value": "Price (₹/Quintal)",
                "variable": "Metric",
            },
            barmode="group",
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
        )

        return fig

    if intent == "transport":
        fig = px.bar(
            data,
            x="warehouse",
            y="average_transit_hours",
            title="Average Transport Time",
            labels={
                "warehouse": "Destination",
                "average_transit_hours": "Average Transit Time (Hours)",
            },
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
        )

        return fig

    return None