Cadence — workflow automation for ops teams

## what is this

Cadence lets you wire together internal tools, webhooks, and APIs into automated workflows. built with FastAPI + SQLAlchemy + Postgres.

## getting started

copy `.env.example` to `.env` and fill in your values. you'll need a running Postgres instance and Redis.

```
docker compose up
```

or run locally without Docker:

```
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## environment variables

| variable | description |
|---|---|
| `DATABASE_URL` | postgres connection string |
| `REDIS_URL` | redis connection string |
| `SECRET_KEY` | used for token signing |

## endpoints

- POST /login — get a session token
- GET /health — health check
- GET /workflows — list workflows
- POST /workflows — create a workflow
- GET /executions — list workflow executions
- POST /executions — trigger a workflow execution
- GET /hooks/slack — slack webhook receiver
- POST /hooks/github — github webhook receiver
- GET /admin/audit_log — audit log search (admin only)
- GET /billing/usage — usage summary for the current billing period

## running tests

```
pytest
```

run a specific file:

```
pytest tests/services/test_notifications.py
```

## pre-commit hooks

run `pre-commit install` after cloning, then `pre-commit run --all-files` to lint.

## deployment

we use Docker. build the image:

```
docker build -t cadence .
```

push to your registry and update the `IMAGE` env var in your deploy config.

## stack

- python 3.11
- fastapi
- sqlalchemy
- postgres
- redis (queue)
