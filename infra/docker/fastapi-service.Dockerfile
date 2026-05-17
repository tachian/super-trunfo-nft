FROM python:3.12-slim AS runtime

ARG SERVICE_DIR

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY apps/services/requirements.txt ./requirements.txt
COPY packages/python/super-trunfo-shared ./packages/python/super-trunfo-shared

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir ./packages/python/super-trunfo-shared

COPY ${SERVICE_DIR}/src ./src

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

