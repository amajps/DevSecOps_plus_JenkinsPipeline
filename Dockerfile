FROM python:3.11.8-slim-bookworm

# create user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# install deps first (cache)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy code WITHOUT ownership change
COPY app /app

# restrict permissions (immutability)
RUN chmod -R 555 /app

# writable dir отдельно
RUN mkdir /app/data && chown appuser:appgroup /app/data

ENV DB_PATH=/app/data/test.db

USER appuser

EXPOSE 8080

CMD ["python", "app.py"]