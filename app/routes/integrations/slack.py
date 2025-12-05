import os
from fastapi import APIRouter, Request, HTTPException
from app.services.integrations.slack import SlackIntegration
from app.services.integrations.retry import with_retries

router = APIRouter()

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


@router.post("/integrations/slack/send")
async def send_slack(request: Request):
    body = await request.json()
    integration = SlackIntegration(webhook_url=SLACK_WEBHOOK_URL)
    try:
        with_retries(lambda: integration.send(body))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"ok": True}
