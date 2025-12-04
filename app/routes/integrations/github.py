import os
from fastapi import APIRouter, Request, HTTPException
from app.services.integrations.github import GitHubIntegration
from app.services.integrations.retry import with_retries

router = APIRouter()


@router.post("/integrations/github/send")
async def send_github(request: Request):
    body = await request.json()
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = body.get("repo", "")
    integration = GitHubIntegration(token=token, repo=repo)
    try:
        with_retries(lambda: integration.send(body))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"ok": True}
