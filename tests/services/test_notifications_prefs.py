import pytest

from app.db import Base, engine, SessionLocal
from app.services.notifications.preferences import get_prefs, set_pref, is_enabled


def setup_function():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from app.models.notification_pref import NotificationPref
    db.query(NotificationPref).delete()
    db.commit()
    db.close()


def test_set_and_get_pref():
    db = SessionLocal()
    pref = set_pref(user_id=1, channel="email", enabled=True, db=db)
    db.close()

    db = SessionLocal()
    prefs = get_prefs(user_id=1, db=db)
    db.close()

    assert len(prefs) == 1
    assert prefs[0].channel == "email"
    assert prefs[0].enabled is True


def test_is_enabled_default_true():
    db = SessionLocal()
    result = is_enabled(user_id=999, channel="email", db=db)
    db.close()
    assert result is True


def test_set_pref_empty_channel_raises():
    db = SessionLocal()
    with pytest.raises(ValueError, match="channel is required"):
        set_pref(user_id=1, channel="", enabled=True, db=db)
    db.close()
