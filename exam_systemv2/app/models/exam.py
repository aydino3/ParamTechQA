from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Integer as SQLInteger, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


class ExamStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class GradingPolicy(str, enum.Enum):
    IMMEDIATE = "immediate"
    AFTER_END = "after_end"
    MANUAL = "manual"


class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    attempts_allowed = Column(Integer, default=1, nullable=False)
    shuffle_questions = Column(Boolean, default=False, nullable=False)
    shuffle_options = Column(Boolean, default=False, nullable=False)
    grading_policy = Column(Enum(GradingPolicy), nullable=False)
    pass_score = Column(Integer, nullable=True)  # percentage
    status = Column(Enum(ExamStatus), default=ExamStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_exams")
    exam_questions = relationship("ExamQuestion", back_populates="exam", order_by="ExamQuestion.sort_order")
    assignments = relationship("Assignment", back_populates="exam")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    sort_order = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    
    # Relationships
    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_questions")

