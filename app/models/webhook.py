import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String)
    events = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
