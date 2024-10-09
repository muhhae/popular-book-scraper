FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    firefox-esr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
