import pytest

# these need a real redis — skipping for now
# from app.services.cache import get, set, delete


@pytest.mark.skip(reason="needs redis running")
def test_set_and_get():
    from app.services.cache import get, set
    set("testkey", "testval", ttl=10)
    assert get("testkey") == "testval"


@pytest.mark.skip(reason="needs redis running")
def test_delete():
    from app.services.cache import set, delete, get
    set("delkey", "v", ttl=10)
    delete("delkey")
    assert get("delkey") is None
