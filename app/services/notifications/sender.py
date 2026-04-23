import logging
import time

from app.services.notifications.loader import render_template

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


def send_notification(user_id: str, template_key: str, context: dict) -> None:
    message = render_template(template_key, context)
    _deliver(user_id, message)


def _deliver(user_id: str, message: str, attempt: int = 0) -> None:
    try:
        logger.info("Notification to user %s: %s", user_id, message)
    except Exception as exc:
        if attempt < _MAX_RETRIES:
            time.sleep(2 ** attempt)
            _deliver(user_id, message, attempt + 1)
        else:
            raise
