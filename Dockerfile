FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .  ← Có dấu cách trước dấu chấm
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .         ← Có dấu cách trước dấu chấm  
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
