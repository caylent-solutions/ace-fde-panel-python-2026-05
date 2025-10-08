Cadence architecture overview

## module map

- app/main.py — FastAPI app, mounts all routers
- app/config.py — reads env vars (DATABASE_URL, REDIS_URL)
- app/db.py — SQLAlchemy engine + session
- app/auth/ — password hashing, session token generation
- app/models/ — SQLAlchemy models (User, Workflow, Run, ApiKey, Integration, Webhook)
- app/routes/ — route handlers
  - app/routes/auth.py — login
  - app/routes/admin/ — admin endpoints (audit log)
  - app/routes/hooks/ — incoming webhook receivers (slack, github)
- app/services/ — business logic
  - app/services/integrations/ — outbound integration handlers (slack, github)
- app/repositories/ — (placeholder, not wired yet)
- app/workers/ — (placeholder, background jobs TBD)
- app/middleware/ — (placeholder)
- app/utils/ — helpers junk drawer (~30 utility functions)
- app/cache/ — redis caching layer at app/cache/ (in progress, see wip branch)

## data stores

- postgres — primary database, all models
- redis — job queue for background workers; redis caching layer at app/cache/ is planned but not fully wired

## request flow

1. request hits FastAPI router
2. route handler pulls a DB session via get_db()
3. handler queries models directly (no repository layer yet)
4. response returned as JSON

## auth

session tokens are random hex strings returned on login. no expiry currently. tokens are not stored server-side yet (stateless check not implemented — this is a known gap).

## integrations

outbound integrations (slack, github) live in app/services/integrations/. they are half-wired — the send() methods construct payloads but don't actually POST yet.

incoming webhooks (slack events, github events) hit app/routes/hooks/ and currently just acknowledge.
