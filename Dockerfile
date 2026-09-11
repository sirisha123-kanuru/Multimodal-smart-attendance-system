FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y \
    openjdk-21-jdk \
    python3 \
    python3-pip \
    python3-venv \
    libgl1 \
    libglib2.0-0 \
    curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend /app/backend
COPY ai /app/ai

# Build Spring Boot
WORKDIR /app/backend
RUN chmod +x mvnw && ./mvnw clean package -DskipTests

# Create Python virtual environment
WORKDIR /app/ai
RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Railway starts both AI and Spring Boot
WORKDIR /app

CMD ["sh", "-c", "cd /app/ai && /opt/venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000 & cd /app/backend && exec java -jar target/*.jar"]