from app.middleware.throttle import check_rate_limit


def test_throttle_exists():
    assert check_rate_limit
