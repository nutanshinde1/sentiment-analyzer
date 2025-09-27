# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# system deps for transformers / tokenizers occasionally
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV HF_HOME=/tmp/hf_cache
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
