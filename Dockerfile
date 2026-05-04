FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --app-dir /app/backend --host 0.0.0.0 --port ${PORT:-8000}"]
