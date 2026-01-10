from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.models.user import User, UserRole
from app.models.exam import Exam
from app.models.question import Question
from app.models.assignment import Assignment
from app.models.attempt import Attempt


class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_stats(self, current_user: User) -> Dict[str, Any]:
        """Get system statistics. Only admins can access."""
        if current_user.role != UserRole.ADMIN:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can access system statistics"
            )
        
        # Count users by role
        total_users = self.db.query(func.count(User.id)).scalar()
        admin_count = self.db.query(func.count(User.id)).filter(User.role == UserRole.ADMIN).scalar()
        teacher_count = self.db.query(func.count(User.id)).filter(User.role == UserRole.TEACHER).scalar()
        student_count = self.db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar()
        active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        
        # Count exams
        from app.models.exam import ExamStatus
        total_exams = self.db.query(func.count(Exam.id)).scalar()
        published_exams = self.db.query(func.count(Exam.id)).filter(Exam.status == ExamStatus.PUBLISHED).scalar()
        draft_exams = self.db.query(func.count(Exam.id)).filter(Exam.status == ExamStatus.DRAFT).scalar()
        
        # Count questions
        total_questions = self.db.query(func.count(Question.id)).scalar()
        
        # Count assignments
        total_assignments = self.db.query(func.count(Assignment.id)).scalar()
        
        # Count attempts
        from app.models.attempt import AttemptStatus
        total_attempts = self.db.query(func.count(Attempt.id)).scalar()
        submitted_attempts = self.db.query(func.count(Attempt.id)).filter(Attempt.status == AttemptStatus.SUBMITTED).scalar()
        
        return {
            "users": {
                "total": total_users,
                "admins": admin_count,
                "teachers": teacher_count,
                "students": student_count,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "exams": {
                "total": total_exams,
                "published": published_exams,
                "draft": draft_exams
            },
            "questions": {
                "total": total_questions
            },
            "assignments": {
                "total": total_assignments
            },
            "attempts": {
                "total": total_attempts,
                "submitted": submitted_attempts
            }
        }
    
    def get_reports(self, current_user: User) -> Dict[str, Any]:
        """Get system reports. Only admins can access."""
        if current_user.role != UserRole.ADMIN:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can access system reports"
            )
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        recent_exams = self.db.query(func.count(Exam.id)).filter(
            Exam.created_at >= thirty_days_ago
        ).scalar()
        
        recent_questions = self.db.query(func.count(Question.id)).filter(
            Question.created_at >= thirty_days_ago
        ).scalar()
        
        recent_attempts = self.db.query(func.count(Attempt.id)).filter(
            Attempt.started_at >= thirty_days_ago
        ).scalar()
        
        return {
            "recent_activity": {
                "last_30_days": {
                    "exams_created": recent_exams,
                    "questions_created": recent_questions,
                    "attempts_started": recent_attempts
                }
            }
        }

