from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.attempt import Attempt, AttemptStatus
from app.models.result import Result
from app.models.assignment import Assignment, AssignmentStatus
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.exam_repository import ExamRepository


class StudentService:
    def __init__(self, db: Session):
        self.attempt_repo = AttemptRepository(db)
        self.result_repo = ResultRepository(db)
        self.assignment_repo = AssignmentRepository(db)
        self.exam_repo = ExamRepository(db)
        self.db = db
    
    def get_student_statistics(self, student: User) -> Dict[str, Any]:
        """Get comprehensive statistics for a student."""
        # Get all attempts
        attempts = self.attempt_repo.list_by_student(student.id)
        submitted_attempts = [a for a in attempts if a.status == AttemptStatus.SUBMITTED]
        
        # Get all results with exam info
        results = []
        results_with_exams = []
        for attempt in submitted_attempts:
            result = self.result_repo.get_by_attempt_id(attempt.id)
            if result and result.released_at:
                results.append(result)
                exam = self.exam_repo.get_by_id(attempt.exam_id)
                results_with_exams.append({
                    'result': result,
                    'exam': exam
                })
        
        # Calculate statistics
        total_completed = len(results)
        total_assignments = len(self.assignment_repo.list_by_student(student.id))
        
        if results:
            percentages = [r.percentage for r in results]
            average_score = sum(percentages) / len(percentages)
            highest_score = max(percentages)
            lowest_score = min(percentages)
            
            # Count passed exams using each exam's pass_score
            passed_exams = 0
            for item in results_with_exams:
                result = item['result']
                exam = item['exam']
                if exam and exam.pass_score is not None:
                    if result.percentage >= exam.pass_score:
                        passed_exams += 1
                else:
                    # Default: 50% if no pass_score set
                    if result.percentage >= 50:
                        passed_exams += 1
            
            pass_rate = (passed_exams / total_completed * 100) if total_completed > 0 else 0
        else:
            average_score = 0
            highest_score = 0
            lowest_score = 0
            pass_rate = 0
        
        # Get exams completed in last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Normalize datetime for comparison
        def normalize_datetime(dt):
            """Normalize datetime to timezone-aware UTC for comparison."""
            if dt is None:
                return None
            if dt.tzinfo is None:
                # Naive datetime - assume UTC
                return dt.replace(tzinfo=timezone.utc)
            # Already timezone-aware, convert to UTC
            return dt.astimezone(timezone.utc)
        
        recent_results = []
        for r in results:
            if r.released_at:
                released_at_normalized = normalize_datetime(r.released_at)
                if released_at_normalized and released_at_normalized >= thirty_days_ago:
                    recent_results.append(r)
        recent_completed = len(recent_results)
        
        return {
            "total_assignments": total_assignments,
            "total_completed": total_completed,
            "average_score": round(average_score, 2),
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "pass_rate": round(pass_rate, 2),
            "recent_completed": recent_completed
        }
    
    def get_upcoming_exams(self, student: User) -> List[Dict[str, Any]]:
        """Get exams that will start soon."""
        assignments = self.assignment_repo.list_by_student(student.id)
        upcoming = []
        now = datetime.now(timezone.utc)
        
        # Normalize datetime for comparison
        def normalize_datetime(dt):
            """Normalize datetime to timezone-aware UTC for comparison."""
            if dt is None:
                return None
            if dt.tzinfo is None:
                # Naive datetime - assume UTC
                return dt.replace(tzinfo=timezone.utc)
            # Already timezone-aware, convert to UTC
            return dt.astimezone(timezone.utc)
        
        for assignment in assignments:
            if assignment.status != AssignmentStatus.ASSIGNED:
                continue
            
            exam = self.exam_repo.get_by_id(assignment.exam_id)
            if not exam:
                continue
            
            # Check if exam starts in the next 7 days
            if exam.start_at:
                start_at_normalized = normalize_datetime(exam.start_at)
                if start_at_normalized and start_at_normalized > now:
                    days_until = (start_at_normalized - now).days
                    if days_until <= 7:
                        upcoming.append({
                            'exam_id': exam.id,
                            'exam_name': exam.name,
                            'start_at': exam.start_at,
                            'days_until': days_until
                        })
        
        # Sort by start_at (normalize for sorting)
        def get_sort_key(x):
            start_at = x['start_at']
            if start_at:
                normalized = normalize_datetime(start_at)
                return normalized if normalized else datetime.min.replace(tzinfo=timezone.utc)
            return datetime.min.replace(tzinfo=timezone.utc)
        
        upcoming.sort(key=get_sort_key)
        return upcoming
    
    def get_exam_attempts_history(self, student: User, exam_id: int) -> List[Dict[str, Any]]:
        """Get all attempts for a specific exam."""
        attempts = self.attempt_repo.list_by_student(student.id)
        exam_attempts = [a for a in attempts if a.exam_id == exam_id]
        
        history = []
        for idx, attempt in enumerate(exam_attempts, 1):
            result = None
            if attempt.status == AttemptStatus.SUBMITTED:
                result = self.result_repo.get_by_attempt_id(attempt.id)
            
            started_at_str = attempt.started_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(attempt.started_at, 'strftime') else str(attempt.started_at)
            status_value = attempt.status.value if hasattr(attempt.status, 'value') else str(attempt.status)
            
            history.append({
                'attempt_id': attempt.id,
                'attempt_number': idx,
                'started_at': started_at_str,
                'status': status_value,
                'score': result.percentage if result and result.released_at else None,
                'earned_points': result.earned_points if result and result.released_at else None,
                'total_points': result.total_points if result and result.released_at else None,
                'released_at': result.released_at.strftime('%Y-%m-%d %H:%M:%S') if result and result.released_at and hasattr(result.released_at, 'strftime') else None
            })
        
        # Sort by started_at descending
        history.sort(key=lambda x: x['started_at'], reverse=True)
        return history

