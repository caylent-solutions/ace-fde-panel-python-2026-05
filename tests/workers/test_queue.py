from unittest.mock import patch, MagicMock
from app.workers import queue as q


def test_enqueue_pushes_to_redis():
    with patch("app.workers.queue.r") as mock_r:
        q.enqueue("send_notification", {"user_id": 1})
        mock_r.rpush.assert_called_once()
        args = mock_r.rpush.call_args[0]
        assert args[0] == q.QUEUE_KEY
        assert "send_notification" in args[1]


def test_dequeue_returns_none_when_empty():
    with patch("app.workers.queue.r") as mock_r:
        mock_r.lpop.return_value = None
        result = q.dequeue()
        assert result is None


def test_dequeue_returns_job():
    import json
    with patch("app.workers.queue.r") as mock_r:
        mock_r.lpop.return_value = json.dumps({"type": "run_workflow", "payload": {"id": 42}}).encode()
        result = q.dequeue()
        assert result["type"] == "run_workflow"
        assert result["payload"]["id"] == 42


def test_queue_length():
    with patch("app.workers.queue.r") as mock_r:
        mock_r.llen.return_value = 5
        assert q.queue_length() == 5
