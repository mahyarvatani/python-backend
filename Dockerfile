FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 APP_VERSION=0.1.0
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd -m appuser
USER appuser
EXPOSE 8888
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]
