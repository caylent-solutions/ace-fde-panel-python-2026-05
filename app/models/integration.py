import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)
    config = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
