# docker/Dockerfile

FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Default command: run all connections sequentially
CMD ["sh", "-c", "python src/workers/connection_worker.py --config config/mappings.yaml --connection-index 0"]
