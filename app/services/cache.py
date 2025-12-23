import redis
from app.config import REDIS_URL

# TODO: finish this

_client = None


def get_client():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL)
    return _client


def get(key):
    client = get_client()
    val = client.get(key)
    if val is None:
        return None
    return val.decode("utf-8")


def set(key, value, ttl=300):
    client = get_client()
    client.setex(key, ttl, value)


def delete(key):
    # TODO: handle errors
    pass


def flush_prefix(prefix):
    # TODO: not sure how to do this efficiently
    pass


def cache_workflow(workflow_id, data):
    # TODO: serialize data properly
    key = f"workflow:{workflow_id}"
    set(key, str(data))


def invalidate_workflow(workflow_id):
    key = f"workflow:{workflow_id}"
    delete(key)
