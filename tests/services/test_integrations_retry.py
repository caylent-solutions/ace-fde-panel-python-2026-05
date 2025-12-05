from unittest.mock import MagicMock, patch
from app.services.integrations.retry import with_retries


def test_with_retries_succeeds_first_try():
    func = MagicMock(return_value="ok")
    result = with_retries(func, max_attempts=3)
    assert result == "ok"
    func.assert_called_once()


def test_with_retries_retries_on_failure():
    func = MagicMock(side_effect=[Exception("boom"), Exception("boom"), "ok"])
    with patch("app.services.integrations.retry.time.sleep"):
        result = with_retries(func, max_attempts=3, base_delay=1)
    assert result == "ok"
    assert func.call_count == 3


def test_with_retries_raises_after_max_attempts():
    func = MagicMock(side_effect=Exception("always fails"))
    with patch("app.services.integrations.retry.time.sleep"):
        try:
            with_retries(func, max_attempts=3)
            assert False, "should have raised"
        except Exception as e:
            assert str(e) == "always fails"
    assert func.call_count == 3


def test_with_retries_exponential_backoff():
    sleep_calls = []
    func = MagicMock(side_effect=[Exception("e"), Exception("e"), "ok"])
    with patch("app.services.integrations.retry.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        with_retries(func, max_attempts=3, base_delay=2)
    assert sleep_calls[0] == 2
    assert sleep_calls[1] == 4
