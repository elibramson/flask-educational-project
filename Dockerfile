FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install system dependencies with retry logic to handle hash sum mismatches
RUN apt-get update --fix-missing \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create instance directory and set proper permissions
RUN mkdir -p /app/instance && \
    chmod 755 /app/instance

RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"] 