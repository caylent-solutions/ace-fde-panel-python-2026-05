FROM python:3.11-slim

# Install PostgreSQL client and build dependencies for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client \
       build-essential \
       python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml requirements.txt .
RUN pip install -e . && pip install -r requirements.txt

COPY . .

CMD ["tail", "-f", "/dev/null"]
