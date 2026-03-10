import logging

from sqlalchemy.orm import Session

from app.models.notification_pref import NotificationPref

logger = logging.getLogger(__name__)


def get_prefs(user_id: int, db: Session) -> list[NotificationPref]:
    return db.query(NotificationPref).filter(NotificationPref.user_id == user_id).all()


def set_pref(user_id: int, channel: str, enabled: bool, db: Session) -> NotificationPref:
    pref = db.query(NotificationPref).filter(
        NotificationPref.user_id == user_id,
        NotificationPref.channel == channel,
    ).first()
    if pref is None:
        pref = NotificationPref(user_id=user_id, channel=channel, enabled=enabled)
        db.add(pref)
    else:
        pref.enabled = enabled
    db.commit()
    db.refresh(pref)
    return pref


def is_enabled(user_id: int, channel: str, db: Session) -> bool:
    pref = db.query(NotificationPref).filter(
        NotificationPref.user_id == user_id,
        NotificationPref.channel == channel,
    ).first()
    if pref is None:
        return True
    return pref.enabled
