import logging

from app.services.notifications.templates import render

logger = logging.getLogger(__name__)


def send_notification(user_id: str, template_key: str, context: dict) -> None:
    message = render(template_key, context)
    logger.info("Notification to user %s: %s", user_id, message)
