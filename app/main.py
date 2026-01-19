from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.hooks import slack_router, github_router
from app.routes.runs import runs_router
from app.routes.workflows import workflows_router

app = FastAPI(title="cadence")

app.include_router(auth_router)
app.include_router(slack_router)
app.include_router(github_router)
app.include_router(runs_router)
app.include_router(workflows_router)


@app.get("/health")
def health():
    return {"ok": True}
