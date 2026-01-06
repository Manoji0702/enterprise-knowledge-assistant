FROM python:3.11-slim

WORKDIR /app

# Copy dependency list first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# 🔴 COPY DOCS BEFORE CMD (THIS WAS MISSING IN EFFECT)
COPY docs /app/app/knowledge/processed

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
