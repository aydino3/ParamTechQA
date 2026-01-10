from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


class AssignmentStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    STARTED = "started"
    SUBMITTED = "submitted"
    GRADED = "graded"


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    exam = relationship("Exam", back_populates="assignments")
    student = relationship("User", back_populates="assignments")
    attempts = relationship("Attempt", back_populates="assignment")

