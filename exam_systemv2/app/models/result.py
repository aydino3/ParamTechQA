from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), unique=True, nullable=False)
    earned_points = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    released_at = Column(DateTime, nullable=True)
    
    # Relationships
    attempt = relationship("Attempt", back_populates="result")

