/**
 * API Client for Mandi-to-Market Supply Chain Optimizer
 */

const API_BASE = "/api";

function buildQueryString(params) {
  const query = new URLSearchParams();
  if (!params) return "";

  if (params.states && params.states.length) {
    params.states.forEach((s) => query.append("states", s));
  }
  if (params.districts && params.districts.length) {
    params.districts.forEach((d) => query.append("districts", d));
  }
  if (params.mandis && params.mandis.length) {
    params.mandis.forEach((m) => query.append("mandis", m));
  }
  if (params.crops && params.crops.length) {
    params.crops.forEach((c) => query.append("crops", c));
  }
  if (params.startDate) {
    query.append("start_date", params.startDate);
  }
  if (params.endDate) {
    query.append("end_date", params.endDate);
  }
  if (params.crop) {
    query.append("crop", params.crop);
  }

  const str = query.toString();
  return str ? `?${str}` : "";
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errData = await res.json();
      errorDetail = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  getHealth: () => fetchJson(`${API_BASE}/health`),
  getFilters: () => fetchJson(`${API_BASE}/filters`),
  getOverview: (filters) => fetchJson(`${API_BASE}/overview${buildQueryString(filters)}`),
  getArrivals: (filters) => fetchJson(`${API_BASE}/arrivals${buildQueryString(filters)}`),
  getPrices: (filters) => fetchJson(`${API_BASE}/prices${buildQueryString(filters)}`),
  getWeather: () => fetchJson(`${API_BASE}/weather`),
  getRisk: (crop) => fetchJson(`${API_BASE}/risk${buildQueryString({ crop })}`),
  getTransport: () => fetchJson(`${API_BASE}/transport`),
  queryAgent: (query) =>
    fetchJson(`${API_BASE}/agent/query`, {
      method: "POST",
      body: JSON.stringify({ query }),
    }),
};
