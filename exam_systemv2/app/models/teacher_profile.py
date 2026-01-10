from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

# Association table for many-to-many relationship between teachers and subjects
teacher_subjects = Table(
    'teacher_subjects',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    subjects = relationship(
        "Subject",
        secondary=teacher_subjects,
        back_populates="teacher_profiles",
        primaryjoin="TeacherProfile.user_id == teacher_subjects.c.teacher_id",
        secondaryjoin="Subject.id == teacher_subjects.c.subject_id"
    )

