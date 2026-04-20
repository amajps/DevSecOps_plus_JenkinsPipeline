FROM python:3.11-slim as builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY app /app

RUN mkdir /app/data && chmod 777 /app/data

ENV DB_PATH=/app/data/test.db

USER appuser

EXPOSE 8080

CMD ["python", "app.py"]