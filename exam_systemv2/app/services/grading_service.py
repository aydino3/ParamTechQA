from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import timezone
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.attempt import AttemptStatus
from app.models.assignment import AssignmentStatus
from app.models.result import Result
from app.models.exam import GradingPolicy
from app.models.user import User, UserRole
from app.core.time import TimeProvider, time_provider
import json


class GradingService:
    def __init__(self, db: Session, time_provider: TimeProvider = None):
        self.attempt_repo = AttemptRepository(db)
        self.result_repo = ResultRepository(db)
        self.exam_repo = ExamRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db
        from app.core.time import time_provider as default_time_provider
        self.time_provider = time_provider if time_provider is not None else default_time_provider
    
    def grade_attempt(self, attempt_id: int) -> Result:
        """Grade an attempt and create result."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        if attempt.status != AttemptStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="Attempt is not submitted")
        
        # Check if result already exists
        existing_result = self.result_repo.get_by_attempt_id(attempt_id)
        if existing_result:
            return existing_result
        
        # Grade the attempt
        snapshots = self.attempt_repo.get_snapshots(attempt_id)
        total_points = sum(s.points for s in snapshots)
        earned_points = 0
        
        for snapshot in snapshots:
            answer = self.attempt_repo.get_answer(attempt_id, snapshot.id)
            if not answer:
                continue
            
            from app.core.utils import safe_json_loads
            correct_answer = safe_json_loads(snapshot.correct_answer_json, default=None)
            if correct_answer is None:
                continue
            
            selected_option = safe_json_loads(answer.selected_option_json, default=answer.selected_option_json)
            
            # Parse options to understand the structure
            options = safe_json_loads(snapshot.options_json, default=[])
            if not isinstance(options, list):
                options = []
            
            # Compare answers
            # correct_answer can be:
            # 1. An index (int) if options were shuffled
            # 2. An option ID (int) if options were not shuffled
            # selected_option can be:
            # 1. An option ID (int or str) from the form
            # 2. An index (int or str) if the form sends index
            
            is_correct = False
            
            if isinstance(correct_answer, int) and options:
                # Check if correct_answer is an index (0-based)
                if 0 <= correct_answer < len(options):
                    # Options were shuffled, correct_answer is an index
                    correct_option = options[correct_answer]
                    if isinstance(correct_option, dict):
                        correct_option_id = correct_option.get("id")
                        # Compare by option ID
                        if isinstance(selected_option, (int, str)):
                            try:
                                selected_id = int(selected_option)
                                is_correct = (correct_option_id == selected_id)
                            except (ValueError, TypeError):
                                is_correct = False
                else:
                    # correct_answer might be an option ID
                    # Find the option with this ID
                    for opt in options:
                        if isinstance(opt, dict) and opt.get("id") == correct_answer:
                            # Compare by option ID
                            if isinstance(selected_option, (int, str)):
                                try:
                                    selected_id = int(selected_option)
                                    is_correct = (correct_answer == selected_id)
                                except (ValueError, TypeError):
                                    is_correct = False
                            break
            else:
                # Fallback: direct comparison
                if isinstance(selected_option, (int, str)) and isinstance(correct_answer, (int, str)):
                    try:
                        is_correct = (int(selected_option) == int(correct_answer))
                    except (ValueError, TypeError):
                        is_correct = (selected_option == correct_answer)
            
            if is_correct:
                earned_points += snapshot.points
        
        percentage = int((earned_points / total_points * 100)) if total_points > 0 else 0
        
        # Determine if result should be released
        exam = self.exam_repo.get_by_id(attempt.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found for attempt")
        
        released_at = None
        if exam.grading_policy == GradingPolicy.IMMEDIATE:
            released_at = self.time_provider.now()
        elif exam.grading_policy == GradingPolicy.AFTER_END:
            # Normalize datetime for comparison
            from app.core.utils import normalize_datetime_to_utc_aware
            now = normalize_datetime_to_utc_aware(self.time_provider.now())
            
            if exam.end_at:
                # Normalize exam.end_at to timezone-aware UTC
                end_at_normalized = normalize_datetime_to_utc_aware(exam.end_at)
                
                if end_at_normalized and now >= end_at_normalized:
                    released_at = self.time_provider.now()
        
        # Check if passed (pass_score is percentage)
        is_passed = False
        if exam.pass_score is not None:
            is_passed = percentage >= exam.pass_score
        else:
            # Default: 50% if no pass_score set
            is_passed = percentage >= 50
        
        result = Result(
            attempt_id=attempt_id,
            earned_points=earned_points,
            total_points=total_points,
            percentage=percentage,
            released_at=released_at
        )
        result = self.result_repo.create(result)
        
        # If result is immediately released (IMMEDIATE policy), update assignment status to GRADED
        if released_at:
            from app.repositories.assignment_repository import AssignmentRepository
            assignment_repo = AssignmentRepository(self.db)
            if attempt.assignment_id:
                assignment = assignment_repo.get_by_id(attempt.assignment_id)
                if assignment:
                    assignment.status = AssignmentStatus.GRADED
                    assignment_repo.update(assignment)
        
        try:
            self.db.commit()
            self.db.refresh(result)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error grading attempt: {str(e)}")
        
        return result
    
    def release_results(self, teacher: User, exam_id: int):
        """Release results for all attempts of an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != teacher.id and teacher.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        attempts = self.attempt_repo.list_by_exam(exam_id)
        
        # Check if all students have completed the exam (all attempts are submitted)
        in_progress_attempts = [a for a in attempts if a.status == AttemptStatus.IN_PROGRESS]
        if in_progress_attempts:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot release results. {len(in_progress_attempts)} student(s) are still taking the exam. Please wait until all students have completed."
            )
        
        now = self.time_provider.now()
        released_count = 0
        
        # Update assignment statuses to GRADED when results are released
        from app.repositories.assignment_repository import AssignmentRepository
        assignment_repo = AssignmentRepository(self.db)
        
        for attempt in attempts:
            if attempt.status != AttemptStatus.SUBMITTED:
                continue
            
            result = self.result_repo.get_by_attempt_id(attempt.id)
            if result and not result.released_at:
                result.released_at = now
                self.result_repo.update(result)
                released_count += 1
                
                # Update assignment status to GRADED
                if attempt.assignment_id:
                    assignment = assignment_repo.get_by_id(attempt.assignment_id)
                    if assignment:
                        assignment.status = AssignmentStatus.GRADED
                        assignment_repo.update(assignment)
        
        # Check if any results were actually released
        if released_count == 0:
            # Check if results are already released
            all_released = all(
                (self.result_repo.get_by_attempt_id(a.id) and 
                 self.result_repo.get_by_attempt_id(a.id).released_at is not None)
                for a in attempts if a.status == AttemptStatus.SUBMITTED
            )
            if all_released:
                raise HTTPException(
                    status_code=400,
                    detail="Results are already released for all submitted attempts."
                )
        
        self.audit_repo.create(
            actor_id=teacher.id,
            action="results_release",
            entity_type="exam",
            entity_id=exam_id
        )
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error releasing results: {str(e)}")
    
    def get_result(self, user: User, attempt_id: int) -> Optional[Result]:
        """Get result for an attempt."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        # Check authorization
        if attempt.student_id != user.id and user.role not in (UserRole.TEACHER, UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        result = self.result_repo.get_by_attempt_id(attempt_id)
        if not result:
            # Auto-grade if not graded yet
            if attempt.status == AttemptStatus.SUBMITTED:
                result = self.grade_attempt(attempt_id)
            else:
                return None
        
        # Check if result is released
        if not result.released_at:
            if user.role == UserRole.STUDENT:
                raise HTTPException(status_code=403, detail="Results not released yet")
        
        return result
    
    def get_exam_results(self, teacher: User, exam_id: int) -> List[dict]:
        """Get all results for an exam. Only teachers/admins can access."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != teacher.id and teacher.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        attempts = self.attempt_repo.list_by_exam(exam_id)
        results = []
        
        for attempt in attempts:
            result = self.result_repo.get_by_attempt_id(attempt.id)
            if result:
                from app.schemas.result import ResultResponse
                results.append({
                    "attempt_id": attempt.id,
                    "student_id": attempt.student_id,
                    "result": ResultResponse.model_validate(result)
                })
        
        return results
    
    def get_exam_statistics(self, teacher: User, exam_id: int) -> dict:
        """Get statistics for an exam. Only teachers/admins can access."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != teacher.id and teacher.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        attempts = self.attempt_repo.list_by_exam(exam_id)
        submitted_attempts = [a for a in attempts if a.status == AttemptStatus.SUBMITTED]
        
        results = []
        for attempt in submitted_attempts:
            result = self.result_repo.get_by_attempt_id(attempt.id)
            if result and result.released_at:
                results.append(result)
        
        if not results:
            return {
                "exam_id": exam_id,
                "total_attempts": len(submitted_attempts),
                "graded_attempts": 0,
                "average_score": 0,
                "median_score": 0,
                "highest_score": 0,
                "lowest_score": 0
            }
        
        percentages = [r.percentage for r in results]
        percentages.sort()
        
        average = sum(percentages) / len(percentages) if percentages else 0
        median = percentages[len(percentages) // 2] if percentages else 0
        
        return {
            "exam_id": exam_id,
            "total_attempts": len(submitted_attempts),
            "graded_attempts": len(results),
            "average_score": round(average, 2),
            "median_score": median,
            "highest_score": max(percentages) if percentages else 0,
            "lowest_score": min(percentages) if percentages else 0
        }
    
    def get_student_results(self, current_user: User, student_id: int) -> List[dict]:
        """Get all results for a student."""
        # Students can only see their own results
        if current_user.role == UserRole.STUDENT and current_user.id != student_id:
            raise HTTPException(status_code=403, detail="You can only view your own results")
        
        attempts = self.attempt_repo.list_by_student(student_id)
        results = []
        
        for attempt in attempts:
            if attempt.status != AttemptStatus.SUBMITTED:
                continue
            
            result = self.result_repo.get_by_attempt_id(attempt.id)
            if result and result.released_at:
                from app.schemas.result import ResultResponse
                results.append({
                    "attempt_id": attempt.id,
                    "exam_id": attempt.exam_id,
                    "result": ResultResponse.model_validate(result)
                })
        
        return results

