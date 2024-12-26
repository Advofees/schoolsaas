
FROM --platform=$TARGETPLATFORM python:3.10-slim as builder

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM --platform=$TARGETPLATFORM python:3.10-slim

WORKDIR /usr/src/app


COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONPATH=/usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY ./backend/ ./backend/
COPY ./alembic/ ./alembic/
COPY ./alembic.ini .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /usr/src/app
USER appuser

EXPOSE 8080

ARG GIT_COMMIT_SHA
ENV GIT_COMMIT_SHA="$GIT_COMMIT_SHA"

CMD ["./backend/start.sh"]