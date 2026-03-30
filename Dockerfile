# Dockerfile — EAPS Flask App
# Build:  docker-compose build
# Run:    docker-compose up -d

FROM python:3.11-slim

WORKDIR /app

# Install system deps (including curl for health checks and gcc for ML libs)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required directories for volumes
RUN mkdir -p data models results

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:5000/ || exit 1

# Run the Flask app via Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "flask_app.server:app"]
