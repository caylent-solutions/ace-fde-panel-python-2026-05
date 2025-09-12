from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/hooks/github")
async def github_hook(request: Request):
    event = request.headers.get("X-GitHub-Event", "")
    body = await request.json()
    # TODO: dispatch based on event type
    return {"event": event, "ok": True}
