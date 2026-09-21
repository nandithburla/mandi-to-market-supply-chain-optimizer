# ==============================================================================
# Multi-Stage Dockerfile for Mandi-to-Market Supply Chain Optimizer
# Stage 1: Build React/Vite SPA
# Stage 2: Python FastAPI Backend + SQLite + Embedded SPA
# ==============================================================================

# ----------------- Stage 1: Frontend Build -----------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ----------------- Stage 2: Python Backend Runner ----------
FROM python:3.11-slim AS runner

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source, data, agent and configuration
COPY src/ ./src/
COPY agent/ ./agent/
COPY dashboard/ ./dashboard/
COPY data/ ./data/
COPY sql/ ./sql/
COPY run_server.py ./

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose server port (8000)
EXPOSE 8000

ENV PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "run_server.py"]
