from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from datetime import timedelta, timezone
import json
import random
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.attempt import Attempt, AttemptQuestionSnapshot, AttemptAnswer, AttemptStatus
from app.models.assignment import AssignmentStatus
from app.models.user import User, UserRole
from app.core.time import TimeProvider, time_provider


class AttemptService:
    def __init__(self, db: Session, time_provider: TimeProvider = None):
        self.attempt_repo = AttemptRepository(db)
        self.assignment_repo = AssignmentRepository(db)
        self.exam_repo = ExamRepository(db)
        self.question_repo = QuestionRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db
        from app.core.time import time_provider as default_time_provider
        self.time_provider = time_provider if time_provider is not None else default_time_provider
    
    def start_attempt(self, student: User, assignment_id: int) -> Attempt:
        """Start an exam attempt (idempotent)."""
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        if assignment.student_id != student.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        exam = self.exam_repo.get_by_id(assignment.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Get current time and normalize for comparison
        from app.core.utils import normalize_datetime_to_utc_aware
        now = normalize_datetime_to_utc_aware(self.time_provider.now())
        
        # Check time window first (more specific error messages)
        start_at_normalized = normalize_datetime_to_utc_aware(exam.start_at)
        end_at_normalized = normalize_datetime_to_utc_aware(exam.end_at)
        
        if start_at_normalized and now < start_at_normalized:
            raise HTTPException(status_code=400, detail="Exam has not started yet")
        if end_at_normalized and now > end_at_normalized:
            raise HTTPException(status_code=400, detail="Exam has ended")
        
        # Check if exam is published (after time checks for better UX)
        from app.models.exam import ExamStatus
        if exam.status != ExamStatus.PUBLISHED:
            raise HTTPException(status_code=400, detail="Exam is not published")
        
        # Idempotent: check for active attempt
        active_attempt = self.attempt_repo.get_active_by_assignment(assignment_id)
        if active_attempt:
            return active_attempt
        
        # Create attempt - count all attempts (including in_progress) for attempt_no
        existing_attempts = self.attempt_repo.list_by_student(student.id)
        all_exam_attempts = [a for a in existing_attempts if a.exam_id == exam.id]
        attempt_no = len(all_exam_attempts) + 1
        # Get current time as naive UTC for database storage
        # time_provider.now() returns timezone-aware UTC, convert to naive UTC
        current_time = self.time_provider.now()
        if current_time.tzinfo is not None:
            # Convert timezone-aware to naive UTC
            started_at = current_time.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            # Already naive, assume UTC
            started_at = current_time
        
        # Calculate ends_at by adding duration to started_at (both naive UTC)
        ends_at = started_at + timedelta(minutes=exam.duration_minutes)
        
        attempt = Attempt(
            exam_id=exam.id,
            student_id=student.id,
            assignment_id=assignment_id,
            attempt_no=attempt_no,
            started_at=started_at,
            ends_at=ends_at,
            status=AttemptStatus.IN_PROGRESS
        )
        attempt = self.attempt_repo.create(attempt)
        self.db.flush()  # Ensure attempt is saved before getting questions
        
        # Create question snapshots
        # Re-fetch exam to ensure we have latest data (in case of transaction isolation issues)
        exam = self.exam_repo.get_by_id(exam.id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        exam_questions = self.exam_repo.get_exam_questions(exam.id)
        if not exam_questions:
            raise HTTPException(status_code=400, detail="Exam has no questions")
        
        # Shuffle if needed (deterministic based on attempt_id)
        question_list = list(exam_questions)
        if exam.shuffle_questions:
            random.seed(attempt.id)
            random.shuffle(question_list)
        
        for idx, eq in enumerate(question_list):
            question = self.question_repo.get_by_id(eq.question_id)
            if not question:
                continue
            
            # Prepare options
            options = []
            correct_answer = None
            for opt in question.options:
                opt_dict = {"id": opt.id, "text": opt.text}
                options.append(opt_dict)
                if opt.is_correct:
                    correct_answer = opt.id
            
            # Shuffle options if needed
            if exam.shuffle_options:
                random.seed(attempt.id * 1000 + idx)
                random.shuffle(options)
                # Update correct_answer to new position
                for i, opt in enumerate(options):
                    if opt["id"] == correct_answer:
                        correct_answer = i
                        break
            
            snapshot = AttemptQuestionSnapshot(
                attempt_id=attempt.id,
                original_question_id=question.id,
                sort_order=idx + 1,
                points=eq.points,
                question_title=question.title,
                question_body=question.body,
                options_json=json.dumps(options),
                correct_answer_json=json.dumps(correct_answer)
            )
            self.attempt_repo.create_snapshot(snapshot)
        
        # Update assignment status
        assignment.status = AssignmentStatus.STARTED
        self.assignment_repo.update(assignment)
        
        self.audit_repo.create(
            actor_id=student.id,
            action="attempt_start",
            entity_type="attempt",
            entity_id=attempt.id
        )
        
        try:
            self.db.commit()
            self.db.refresh(attempt)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error starting attempt: {str(e)}")
        
        return attempt
    
    def save_answer(self, student: User, attempt_id: int, snapshot_id: int, selected_option: Any):
        """Save or update an answer."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        if attempt.student_id != student.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Attempt is not in progress")
        
        # Check time
        # Both attempt.ends_at (naive UTC) and now (timezone-aware UTC) need to be compared
        now = self.time_provider.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)
        
        if attempt.ends_at:
            # attempt.ends_at is stored as naive UTC, convert to timezone-aware UTC
            ends_at_normalized = attempt.ends_at.replace(tzinfo=timezone.utc)
            
            if now > ends_at_normalized:
                attempt.status = AttemptStatus.EXPIRED
                self.attempt_repo.update(attempt)
                self.db.commit()
                raise HTTPException(status_code=400, detail="Time has expired")
        
        # Ensure answered_at is naive datetime for database storage
        answered_at = now.replace(tzinfo=None)
        
        answer = AttemptAnswer(
            attempt_id=attempt_id,
            snapshot_id=snapshot_id,
            selected_option_json=json.dumps(selected_option),
            answered_at=answered_at
        )
        self.attempt_repo.create_or_update_answer(answer)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")
    
    def submit_attempt(self, student: User, attempt_id: int) -> Attempt:
        """Submit an attempt (idempotent)."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        if attempt.student_id != student.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Idempotent: if already submitted, return it
        if attempt.status == AttemptStatus.SUBMITTED:
            return attempt
        
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Attempt cannot be submitted")
        
        # Check if time has expired
        # Both attempt.ends_at (naive UTC) and now (timezone-aware UTC) need to be compared
        now = self.time_provider.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)
        
        if attempt.ends_at:
            # attempt.ends_at is stored as naive UTC, convert to timezone-aware UTC
            ends_at_normalized = attempt.ends_at.replace(tzinfo=timezone.utc)
            
            if now > ends_at_normalized:
                # Time expired, auto-submit
                attempt.status = AttemptStatus.SUBMITTED
                # Ensure submitted_at is naive datetime for database storage
                submitted_at = now.replace(tzinfo=None)
                attempt.submitted_at = submitted_at
                self.attempt_repo.update(attempt)
                self.db.flush()  # Ensure attempt is saved before counting
                
                assignment = self.assignment_repo.get_by_id(attempt.assignment_id)
                if assignment:
                    # Reset to ASSIGNED so student can start again (no attempt limit)
                    assignment.status = AssignmentStatus.ASSIGNED
                    self.assignment_repo.update(assignment)
                
                try:
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    raise HTTPException(status_code=500, detail=f"Error auto-submitting attempt: {str(e)}")
                
                raise HTTPException(status_code=400, detail="Time has expired. Your exam was automatically submitted.")
        
        # Ensure submitted_at is naive datetime for database storage
        submitted_at = now.replace(tzinfo=None)
        attempt.submitted_at = submitted_at
        attempt.status = AttemptStatus.SUBMITTED
        
        # Update attempt
        self.attempt_repo.update(attempt)
        
        assignment = self.assignment_repo.get_by_id(attempt.assignment_id)
        if assignment:
            # Reset to ASSIGNED so student can start again (no attempt limit)
            assignment.status = AssignmentStatus.ASSIGNED
            self.assignment_repo.update(assignment)
        
        self.audit_repo.create(
            actor_id=student.id,
            action="attempt_submit",
            entity_type="attempt",
            entity_id=attempt.id
        )
        
        try:
            self.db.commit()
            self.db.refresh(attempt)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error submitting attempt: {str(e)}")
        
        return attempt
    
    def get_attempt_with_questions(self, student: User, attempt_id: int) -> Dict[str, Any]:
        """Get attempt with question snapshots and answers."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        # Allow students to see their own attempts, or teachers/admins to see any attempt
        if attempt.student_id != student.id and student.role not in (UserRole.TEACHER, UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if time has expired
        # Both attempt.ends_at (naive UTC) and now (timezone-aware UTC) need to be compared
        now = self.time_provider.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)
        
        if attempt.status == AttemptStatus.IN_PROGRESS and attempt.ends_at:
            # attempt.ends_at is stored as naive UTC, convert to timezone-aware UTC
            ends_at_normalized = attempt.ends_at.replace(tzinfo=timezone.utc)
            
            if now > ends_at_normalized:
                # Auto-submit if time expired
                if attempt.status == AttemptStatus.IN_PROGRESS:
                    attempt.status = AttemptStatus.SUBMITTED
                    # Ensure submitted_at is naive datetime for database storage
                    from app.core.utils import normalize_datetime_to_utc_naive
                    submitted_at = normalize_datetime_to_utc_naive(now)
                    attempt.submitted_at = submitted_at
                    self.attempt_repo.update(attempt)
                    
                    # Update assignment status
                    assignment = self.assignment_repo.get_by_id(attempt.assignment_id)
                    if assignment:
                        # Reset to ASSIGNED so student can start again (no attempt limit)
                        assignment.status = AssignmentStatus.ASSIGNED
                        self.assignment_repo.update(assignment)
                    
                    try:
                        self.db.commit()
                    except Exception as e:
                        self.db.rollback()
                        raise HTTPException(status_code=500, detail=f"Error auto-submitting attempt: {str(e)}")
        
        snapshots = self.attempt_repo.get_snapshots(attempt_id)
        questions = []
        for snapshot in snapshots:
            try:
                answer = self.attempt_repo.get_answer(attempt_id, snapshot.id)
                
                # Parse options JSON safely
                from app.core.utils import safe_json_loads
                options = safe_json_loads(snapshot.options_json, default=[])
                if not isinstance(options, list):
                    options = []
                
                # Parse answer JSON safely
                answer_value = None
                if answer and answer.selected_option_json:
                    answer_value = safe_json_loads(answer.selected_option_json, default=answer.selected_option_json)
                
                # Parse correct_answer_json to find the correct option
                correct_answer_value = safe_json_loads(snapshot.correct_answer_json, default=None)
                
                # Find correct option based on correct_answer_value
                # correct_answer_value can be an index (int) or option id (int)
                correct_option = None
                if correct_answer_value is not None and options:
                    if isinstance(correct_answer_value, int):
                        # If it's an index (0-based)
                        if 0 <= correct_answer_value < len(options):
                            correct_option = options[correct_answer_value]
                        else:
                            # Try to find by id
                            for opt in options:
                                if isinstance(opt, dict) and opt.get("id") == correct_answer_value:
                                    correct_option = opt
                                    break
                    else:
                        # Try to find by id
                        for opt in options:
                            if isinstance(opt, dict) and opt.get("id") == correct_answer_value:
                                correct_option = opt
                                break
                
                q_data = {
                    "id": snapshot.id,
                    "snapshot_id": snapshot.id,
                    "sort_order": snapshot.sort_order,
                    "points": snapshot.points,
                    "question_title": snapshot.question_title or "",
                    "question_body": snapshot.question_body or "",
                    "options": options,
                    "answer": answer_value,
                    "correct_answer": correct_option.get("id") if correct_option and isinstance(correct_option, dict) else correct_answer_value,
                    "correct_answer_text": correct_option.get("text") if correct_option and isinstance(correct_option, dict) else None
                }
                questions.append(q_data)
            except Exception as e:
                # Skip problematic snapshots
                continue
        
        return {
            "attempt": attempt,
            "questions": questions
        }

