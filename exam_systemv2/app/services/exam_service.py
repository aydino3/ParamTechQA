from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.exam import Exam, ExamQuestion, ExamStatus
from app.models.user import User, UserRole
from app.schemas.exam import ExamCreate, ExamUpdate, ExamQuestionCreate
from app.core.time import time_provider
from datetime import timezone


class ExamService:
    def __init__(self, db: Session):
        self.exam_repo = ExamRepository(db)
        self.question_repo = QuestionRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db
    
    def create_exam(self, owner: User, data: ExamCreate) -> Exam:
        """Create a new exam."""
        # Validate duration_minutes
        if data.duration_minutes <= 0:
            raise HTTPException(status_code=400, detail="Duration must be greater than 0")
        
        # Validate attempts_allowed
        if data.attempts_allowed <= 0:
            raise HTTPException(status_code=400, detail="Attempts allowed must be greater than 0")
        
        # Validate pass_score
        if data.pass_score is not None:
            if data.pass_score < 0 or data.pass_score > 100:
                raise HTTPException(status_code=400, detail="Pass score must be between 0 and 100")
        
        # Validate start_at and end_at
        from app.core.utils import normalize_datetime_to_utc_aware
        now = normalize_datetime_to_utc_aware(time_provider.now())
        
        if data.start_at:
            # Normalize start_at for comparison
            start_at_normalized = normalize_datetime_to_utc_aware(data.start_at)
            
            if start_at_normalized and start_at_normalized < now:
                raise HTTPException(status_code=400, detail="Start date cannot be in the past")
        
        if data.end_at:
            # Normalize end_at for comparison
            end_at_normalized = normalize_datetime_to_utc_aware(data.end_at)
            
            if end_at_normalized and end_at_normalized < now:
                raise HTTPException(status_code=400, detail="End date cannot be in the past")
        
        if data.start_at and data.end_at:
            if data.end_at <= data.start_at:
                raise HTTPException(status_code=400, detail="End date must be after start date")
        
        exam = Exam(
            owner_id=owner.id,
            name=data.name,
            description=data.description,
            duration_minutes=data.duration_minutes,
            start_at=data.start_at,
            end_at=data.end_at,
            attempts_allowed=data.attempts_allowed,
            shuffle_questions=data.shuffle_questions,
            shuffle_options=data.shuffle_options,
            grading_policy=data.grading_policy,
            pass_score=data.pass_score
        )
        exam = self.exam_repo.create(exam)
        
        self.audit_repo.create(
            actor_id=owner.id,
            action="exam_create",
            entity_type="exam",
            entity_id=exam.id
        )
        
        try:
            self.db.commit()
            self.db.refresh(exam)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating exam: {str(e)}")
        
        return exam
    
    def update_exam(self, owner: User, exam_id: int, data: ExamUpdate) -> Exam:
        """Update an existing exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if exam is published - published exams cannot be edited
        if exam.status == ExamStatus.PUBLISHED:
            raise HTTPException(
                status_code=400, 
                detail="Cannot edit a published exam. Please unpublish it first if you need to make changes."
            )
        
        # Validate duration_minutes
        if data.duration_minutes is not None and data.duration_minutes <= 0:
            raise HTTPException(status_code=400, detail="Duration must be greater than 0")
        
        # Validate attempts_allowed
        if data.attempts_allowed is not None and data.attempts_allowed <= 0:
            raise HTTPException(status_code=400, detail="Attempts allowed must be greater than 0")
        
        # Validate pass_score
        if data.pass_score is not None:
            if data.pass_score < 0 or data.pass_score > 100:
                raise HTTPException(status_code=400, detail="Pass score must be between 0 and 100")
        
        # Validate start_at and end_at
        start_at = data.start_at if data.start_at is not None else exam.start_at
        end_at = data.end_at if data.end_at is not None else exam.end_at
        if start_at and end_at:
            if end_at <= start_at:
                raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if data.name is not None:
            exam.name = data.name
        if data.description is not None:
            exam.description = data.description
        if data.duration_minutes is not None:
            exam.duration_minutes = data.duration_minutes
        if data.start_at is not None:
            exam.start_at = data.start_at
        if data.end_at is not None:
            exam.end_at = data.end_at
        if data.attempts_allowed is not None:
            exam.attempts_allowed = data.attempts_allowed
        if data.shuffle_questions is not None:
            exam.shuffle_questions = data.shuffle_questions
        if data.shuffle_options is not None:
            exam.shuffle_options = data.shuffle_options
        if data.grading_policy is not None:
            exam.grading_policy = data.grading_policy
        if data.pass_score is not None:
            exam.pass_score = data.pass_score
        if data.status is not None:
            exam.status = data.status
            if data.status == ExamStatus.PUBLISHED:
                self.audit_repo.create(
                    actor_id=owner.id,
                    action="exam_publish",
                    entity_type="exam",
                    entity_id=exam.id
                )
        
        self.exam_repo.update(exam)
        self.db.commit()
        
        return exam
    
    def add_question_to_exam(self, owner: User, exam_id: int, data: ExamQuestionCreate) -> ExamQuestion:
        """Add a question to an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        question = self.question_repo.get_by_id(data.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if question.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Question not owned by you")
        
        # Check if question is already in the exam
        exam_questions = self.exam_repo.get_exam_questions(exam_id)
        existing_question = next((eq for eq in exam_questions if eq.question_id == data.question_id), None)
        if existing_question:
            raise HTTPException(
                status_code=400,
                detail="This question is already in the exam. Each question can only be added once."
            )
        
        # Validate points
        if data.points <= 0:
            raise HTTPException(status_code=400, detail="Points must be greater than 0")
        
        # Check for duplicate sort_order
        existing_sort_order = next((eq for eq in exam_questions if eq.sort_order == data.sort_order), None)
        if existing_sort_order:
            raise HTTPException(
                status_code=400,
                detail=f"Sort order {data.sort_order} is already used by another question. Please choose a different sort order."
            )
        
        exam_question = ExamQuestion(
            exam_id=exam_id,
            question_id=data.question_id,
            sort_order=data.sort_order,
            points=data.points
        )
        exam_question = self.exam_repo.add_exam_question(exam_question)
        
        try:
            self.db.commit()
            self.db.refresh(exam_question)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding question to exam: {str(e)}")
        
        return exam_question
    
    def list_exams(
        self, 
        owner: User, 
        skip: int = 0, 
        limit: int = 100,
        sort: Optional[str] = "created_at",
        order: Optional[str] = "desc"
    ) -> tuple[List[Exam], int]:
        """List exams owned by the user with sorting. Returns (exams, total_count)."""
        from sqlalchemy import desc, asc
        
        query = self.db.query(Exam).filter(Exam.owner_id == owner.id)
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort == "name":
            sort_field = Exam.name
        elif sort == "created_at":
            sort_field = Exam.created_at
        else:
            sort_field = Exam.created_at
        
        if order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        exams = query.offset(skip).limit(limit).all()
        return (exams, total)
    
    def get_exam(self, owner: User, exam_id: int) -> Exam:
        """Get an exam by ID."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return exam
    
    def delete_exam(self, owner: User, exam_id: int) -> dict:
        """Delete an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if any students have started the exam
        from app.repositories.attempt_repository import AttemptRepository
        attempt_repo = AttemptRepository(self.db)
        attempts = attempt_repo.list_by_exam(exam_id)
        
        if attempts and len(attempts) > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete an exam that has attempts. Please archive it instead."
            )
        
        # Manually delete related records (cascade delete not configured)
        # Delete exam_questions
        exam_questions = self.exam_repo.get_exam_questions(exam_id)
        for eq in exam_questions:
            self.db.delete(eq)
        
        # Delete assignments (only if no attempts exist)
        from app.repositories.assignment_repository import AssignmentRepository
        assignment_repo = AssignmentRepository(self.db)
        assignments = assignment_repo.list_by_exam(exam_id)
        for assignment in assignments:
            self.db.delete(assignment)
        
        # Delete the exam
        self.db.delete(exam)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting exam: {str(e)}")
        
        return {"message": "Exam deleted successfully"}
    
    def remove_question_from_exam(self, owner: User, exam_id: int, question_id: int) -> dict:
        """Remove a question from an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        exam_questions = self.exam_repo.get_exam_questions(exam_id)
        exam_question = next((eq for eq in exam_questions if eq.question_id == question_id), None)
        
        if not exam_question:
            raise HTTPException(status_code=404, detail="Question not found in exam")
        
        self.exam_repo.remove_exam_question(exam_question)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error removing question from exam: {str(e)}")
        
        return {"message": "Question removed from exam"}
    
    def publish_exam(self, owner: User, exam_id: int) -> Exam:
        """Publish an exam. Can publish from DRAFT or ARCHIVED status."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if exam has at least one question
        exam_questions = self.exam_repo.get_exam_questions(exam_id)
        if not exam_questions or len(exam_questions) == 0:
            raise HTTPException(status_code=400, detail="Cannot publish an exam without questions. Please add at least one question first.")
        
        # Allow publishing from DRAFT or ARCHIVED status
        if exam.status not in (ExamStatus.DRAFT, ExamStatus.ARCHIVED):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish an exam with status {exam.status.value}. Only DRAFT or ARCHIVED exams can be published."
            )
        
        exam.status = ExamStatus.PUBLISHED
        self.exam_repo.update(exam)
        
        self.audit_repo.create(
            actor_id=owner.id,
            action="exam_publish",
            entity_type="exam",
            entity_id=exam.id
        )
        
        try:
            self.db.commit()
            self.db.refresh(exam)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error publishing exam: {str(e)}")
        
        return exam
    
    def unpublish_exam(self, owner: User, exam_id: int) -> Exam:
        """Unpublish an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        exam.status = ExamStatus.DRAFT
        self.exam_repo.update(exam)
        
        try:
            self.db.commit()
            self.db.refresh(exam)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error unpublishing exam: {str(e)}")
        
        return exam
    
    def archive_exam(self, owner: User, exam_id: int) -> Exam:
        """Archive an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        exam.status = ExamStatus.ARCHIVED
        self.exam_repo.update(exam)
        
        try:
            self.db.commit()
            self.db.refresh(exam)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error archiving exam: {str(e)}")
        
        return exam
    
    def get_exam_assignments(self, owner: User, exam_id: int) -> List:
        """Get assignments for an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        from app.repositories.assignment_repository import AssignmentRepository
        assignment_repo = AssignmentRepository(self.db)
        assignments = assignment_repo.list_by_exam(exam_id)
        
        from app.schemas.assignment import AssignmentResponse
        return [AssignmentResponse.model_validate(a) for a in assignments]
    
    def get_exam_statistics(self, owner: User, exam_id: int) -> dict:
        """Get statistics for an exam."""
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        from app.repositories.assignment_repository import AssignmentRepository
        from app.models.attempt import Attempt, AttemptStatus
        
        assignment_repo = AssignmentRepository(self.db)
        assignments = assignment_repo.list_by_exam(exam_id)
        
        total_assignments = len(assignments)
        
        # Get attempts for this exam
        attempts = self.db.query(Attempt).filter(Attempt.exam_id == exam_id).all()
        total_attempts = len(attempts)
        submitted_attempts = len([a for a in attempts if a.status == AttemptStatus.SUBMITTED])
        
        return {
            "exam_id": exam_id,
            "total_assignments": total_assignments,
            "total_attempts": total_attempts,
            "submitted_attempts": submitted_attempts,
            "completion_rate": round((submitted_attempts / total_assignments * 100) if total_assignments > 0 else 0, 2)
        }

