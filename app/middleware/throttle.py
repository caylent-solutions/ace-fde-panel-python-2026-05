import time

# TODO: move to redis — this only works with a single process

_BUCKET: dict = {}

WINDOW_SECONDS = 60
MAX_REQUESTS = 100


def check_rate_limit(api_key: str):
    now = time.time()
    if api_key not in _BUCKET:
        _BUCKET[api_key] = []

    # keep timestamps inside the window
    _BUCKET[api_key] = [t for t in _BUCKET[api_key] if now - t < WINDOW_SECONDS]

    if len(_BUCKET[api_key]) >= MAX_REQUESTS:
        # should return 429 but returning None for now
        return None

    _BUCKET[api_key].append(now)
    return True
