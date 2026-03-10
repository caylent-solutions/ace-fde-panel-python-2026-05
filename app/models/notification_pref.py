from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class NotificationPref(Base):
    __tablename__ = "notification_prefs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel = Column(String, nullable=False, default="email")
    enabled = Column(Boolean, default=True)
