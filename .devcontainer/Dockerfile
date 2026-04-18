FROM python:3.11-slim

# Match the postgres major in docker-compose.yml so psql in the dev
# container talks the same wire version as the db service.
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-14 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml .
RUN pip install -e .

COPY . .
