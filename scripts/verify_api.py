import urllib.request
import json

def test_get(url):
    req = urllib.request.urlopen(url)
    data = req.read().decode("utf-8")
    return req.status, data

def test_post(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req)
    return resp.status, json.loads(resp.read().decode("utf-8"))

print("=== 1. Health Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/health")
print("Status:", status, json.loads(body)["status"])

print("=== 2. SPA Root HTML ===")
status, body = test_get("http://127.0.0.1:8000/")
print("SPA Status:", status, "Contains Mandi-to-Market:", "Mandi-to-Market" in body)

print("=== 3. Overview Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/overview")
print("Overview KPIs:", json.loads(body)["kpis"])

print("=== 4. Arrivals Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/arrivals")
print("Arrivals KPIs:", json.loads(body)["kpis"], "Mandi count:", len(json.loads(body)["mandi_table"]))

print("=== 5. Prices Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/prices")
print("Prices KPIs:", json.loads(body)["kpis"])

print("=== 6. Weather Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/weather")
print("Weather KPIs:", json.loads(body)["kpis"], "Correlations:", json.loads(body)["correlations"])

print("=== 7. Risk Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/risk")
print("Risk categories:", json.loads(body)["category_counts"], "Risk rankings count:", len(json.loads(body)["risk_rankings"]))

print("=== 8. Transport Endpoint ===")
status, body = test_get("http://127.0.0.1:8000/api/transport")
print("Transport KPIs:", json.loads(body)["kpis"], "Warehouses:", len(json.loads(body)["warehouse_delays"]))

print("=== 9. AI Assistant Queries ===")
queries = [
    "Which mandis have the highest wheat arrivals?",
    "Which mandis have wheat prices below MSP?",
    "What is the average rainfall and temperature?",
    "Show me the transport delays."
]
for q in queries:
    st, res = test_post("http://127.0.0.1:8000/api/agent/query", {"query": q})
    ans = res.get('answer', '')[:75].encode('ascii', 'replace').decode('ascii')
    print(f"Query: \"{q}\" -> Intent: {res.get('intent')} | Answer preview: {ans}...")

print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
