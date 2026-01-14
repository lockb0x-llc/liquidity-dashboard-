FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed (e.g. for building some python packages)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
EXPOSE 8000

RUN chmod +x start.sh

CMD ["./start.sh"]
