import pytest
from unittest.mock import patch

from app.services.notifications.sender import send_notification
from app.services.notifications.loader import render_template
from app.services.notifications.templates import render


def test_render_run_complete():
    result = render("run_complete", {"run_name": "daily-sync"})
    assert result == "Your run 'daily-sync' has completed."


def test_send_notification_logs(caplog):
    import logging
    with caplog.at_level(logging.INFO, logger="app.services.notifications.sender"):
        send_notification("user-42", "run_complete", {"run_name": "daily-sync"})
    assert "daily-sync" in caplog.text


def test_render_template_unknown_key():
    with pytest.raises(ValueError, match="Unknown template"):
        render_template("nonexistent_key", {})


def test_render_template_empty_context():
    with pytest.raises(KeyError):
        render_template("run_complete", {})
