import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    output = Column(Text)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
