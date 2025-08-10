from fastapi import FastAPI

app = FastAPI(title="cadence")


@app.get("/health")
def health():
    return {"ok": True}
