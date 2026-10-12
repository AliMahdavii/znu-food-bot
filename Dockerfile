
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

COPY . .

CMD ["python", "main.py"]