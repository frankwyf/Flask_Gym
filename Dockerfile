FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance Loggings

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import sys, urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3); sys.exit(0)" || exit 1

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8000", "run:app"]
