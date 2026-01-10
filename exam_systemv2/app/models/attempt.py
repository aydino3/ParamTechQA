from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Text, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EXPIRED = "expired"


class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    attempt_no = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(Enum(AttemptStatus), default=AttemptStatus.IN_PROGRESS, nullable=False)
    
    # Relationships
    exam = relationship("Exam")
    student = relationship("User", back_populates="attempts")
    assignment = relationship("Assignment", back_populates="attempts")
    question_snapshots = relationship("AttemptQuestionSnapshot", back_populates="attempt", order_by="AttemptQuestionSnapshot.sort_order")
    answers = relationship("AttemptAnswer", back_populates="attempt")
    result = relationship("Result", back_populates="attempt", uselist=False)


class AttemptQuestionSnapshot(Base):
    __tablename__ = "attempt_question_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False)
    original_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    sort_order = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    question_title = Column(String, nullable=False)
    question_body = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON string
    correct_answer_json = Column(Text, nullable=False)  # JSON string
    
    # Relationships
    attempt = relationship("Attempt", back_populates="question_snapshots")
    answers = relationship("AttemptAnswer", back_populates="snapshot")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False)
    snapshot_id = Column(Integer, ForeignKey("attempt_question_snapshots.id"), nullable=False)
    selected_option_json = Column(Text, nullable=False)  # JSON string
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    attempt = relationship("Attempt", back_populates="answers")
    snapshot = relationship("AttemptQuestionSnapshot", back_populates="answers")

