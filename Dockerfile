FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgirepository1.0-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libffi-dev \
    shared-mime-info \
    libgdk-pixbuf2.0-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]
