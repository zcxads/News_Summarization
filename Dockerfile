# Build Stage for React Frontend
FROM node:20 AS build-stage
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Production Stage for Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn

# Copy built frontend assets from build-stage
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# Copy backend source code and main entry point
COPY backend/ ./backend/
COPY main.py .

# Ensure data directory exists for SQLite
RUN mkdir -p backend/data

# Expose port
EXPOSE 8000

# Run the application from root
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
