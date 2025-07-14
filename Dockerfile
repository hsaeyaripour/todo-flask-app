FROM python:3.11-slim

# جلوگیری از تعامل با ورودی (مناسب برای CI/CD و اجرای غیرتعاملی)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# نصب ابزارهای ضروری (اختیاری ولی مفید)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "app.py"]
