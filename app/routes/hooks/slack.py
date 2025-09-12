from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/hooks/slack")
async def slack_hook(request: Request):
    body = await request.json()
    event_type = body.get("type", "")
    if event_type == "url_verification":
        return {"challenge": body.get("challenge")}
    # TODO: dispatch to handler
    return {"ok": True}
