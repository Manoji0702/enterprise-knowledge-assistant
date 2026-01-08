FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend
COPY app ./app

# Frontend
COPY app/web ./web

# 🔴 IMPORTANT: bake docs back into image (old working way)
COPY docs ./app/knowledge/seed

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
