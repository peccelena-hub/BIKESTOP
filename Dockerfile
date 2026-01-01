# -------- Stage 1: build frontend --------
FROM node:18-alpine AS fe
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# -------- Stage 2: backend + serve frontend --------
FROM python:3.11-slim AS be
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY --from=fe /app/frontend/dist /app/frontend_dist
ENV FRONTEND_DIST=/app/frontend_dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
