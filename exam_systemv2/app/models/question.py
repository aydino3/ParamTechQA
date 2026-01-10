from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5
    type = Column(Enum(QuestionType), nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    tags = relationship("QuestionTag", back_populates="question", cascade="all, delete-orphan")
    exam_questions = relationship("ExamQuestion", back_populates="question")


class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Integer, default=0, nullable=False)  # 0 or 1 for SQLite compatibility
    
    # Relationships
    question = relationship("Question", back_populates="options")


class QuestionTag(Base):
    __tablename__ = "question_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    tag = Column(String, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="tags")

