FROM ubuntu:24.04

# Install Java 21, Python, pip and required OpenCV libraries
RUN apt-get update && \
    apt-get install -y \
    openjdk-21-jdk \
    python3 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Application directory
WORKDIR /app

# Copy backend and AI projects
COPY backend /app/backend
COPY ai /app/ai

# Build Spring Boot application
WORKDIR /app/backend

RUN chmod +x mvnw && \
    ./mvnw clean package -DskipTests

# Install Python dependencies
WORKDIR /app/ai

RUN python3 -m pip install \
    --break-system-packages \
    --no-cache-dir \
    -r requirements.txt

# Start both FastAPI and Spring Boot
WORKDIR /app

CMD ["sh", "-c", "cd /app/ai && python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 & sleep 3; cd /app/backend && exec java -jar target/*.jar"]