Cadence — workflow automation for ops teams

## what is this

Cadence lets you wire together internal tools, webhooks, and APIs into automated workflows. built with FastAPI + SQLAlchemy + Postgres.

## getting started

copy .env.example to .env and fill in your values, then:

```
docker compose up
```

or run locally:

```
uvicorn app.main:app --reload
```

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

## running tests

```
pytest
```

## pre-commit hooks

run `pre-commit install` after cloning, then `pre-commit run --all-files` to lint.

## stack

- python 3.11
- fastapi
- sqlalchemy
- postgres
- redis (queue)
