import redis
from app.config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL)

QUEUE_KEY = "cadence:jobs"


def enqueue(job_type: str, payload: dict):
    import json
    data = json.dumps({"type": job_type, "payload": payload})
    r.rpush(QUEUE_KEY, data)


def dequeue():
    import json
    item = r.lpop(QUEUE_KEY)
    if item is None:
        return None
    return json.loads(item)


def queue_length():
    return r.llen(QUEUE_KEY)
