import time
from typing import Callable, Any

# TODO: handle 429 rate limit responses — need to respect Retry-After header


def with_retries(func: Callable, max_attempts=3, base_delay=1) -> Any:
    attempt = 0
    while attempt < max_attempts:
        try:
            return func()
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)
