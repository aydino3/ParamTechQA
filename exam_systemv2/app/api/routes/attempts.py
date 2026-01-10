from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from app.db.session import get_db
from app.services.attempt_service import AttemptService
from app.services.grading_service import GradingService
from app.schemas.attempt import AttemptStartResponse, AnswerSubmit, AttemptResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/start", response_model=AttemptResponse)
def start_attempt(
    assignment_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Start an exam attempt."""
    service = AttemptService(db)
    attempt = service.start_attempt(current_user, assignment_id)
    return attempt


@router.post("/{attempt_id}/answer")
def save_answer(
    attempt_id: int,
    answer: AnswerSubmit,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Save an answer."""
    service = AttemptService(db)
    service.save_answer(current_user, attempt_id, answer.snapshot_id, answer.selected_option)
    return {"message": "Answer saved"}


@router.post("/{attempt_id}/submit", response_model=AttemptResponse)
def submit_attempt(
    attempt_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Submit an attempt."""
    attempt_service = AttemptService(db)
    attempt = attempt_service.submit_attempt(current_user, attempt_id)
    
    # Auto-grade if policy is IMMEDIATE
    grading_service = GradingService(db)
    grading_service.grade_attempt(attempt_id)
    
    return attempt


@router.get("/{attempt_id}", response_model=dict)
def get_attempt(
    attempt_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Get attempt with questions."""
    service = AttemptService(db)
    return service.get_attempt_with_questions(current_user, attempt_id)


@router.get("/", response_model=List[dict])
def list_attempts(
    student_id: Optional[int] = Query(None),
    exam_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List attempts with filtering. Students can only see their own attempts."""
    from app.repositories.attempt_repository import AttemptRepository
    attempt_repo = AttemptRepository(db)
    
    if current_user.role == UserRole.STUDENT:
        # Students can only see their own attempts
        attempts = attempt_repo.list_by_student(current_user.id)
    elif student_id:
        # Teachers/Admins can filter by student
        attempts = attempt_repo.list_by_student(student_id)
    elif exam_id:
        # Teachers/Admins can filter by exam
        attempts = attempt_repo.list_by_exam(exam_id)
    else:
        # Need at least one filter
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify student_id or exam_id"
        )
    
    return [
        {
            "id": a.id,
            "exam_id": a.exam_id,
            "student_id": a.student_id,
            "status": a.status.value,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None
        }
        for a in attempts
    ]


@router.get("/students/{student_id}", response_model=List[dict])
def get_student_attempts(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all attempts for a student."""
    from app.repositories.attempt_repository import AttemptRepository
    attempt_repo = AttemptRepository(db)
    
    # Students can only see their own attempts
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own attempts"
        )
    
    attempts = attempt_repo.list_by_student(student_id)
    return [
        {
            "id": a.id,
            "exam_id": a.exam_id,
            "status": a.status.value,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None
        }
        for a in attempts
    ]


@router.get("/exams/{exam_id}", response_model=List[dict])
def get_exam_attempts(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get all attempts for an exam. Only teachers/admins can access."""
    from app.repositories.attempt_repository import AttemptRepository
    from app.repositories.exam_repository import ExamRepository
    from fastapi import HTTPException, status
    
    attempt_repo = AttemptRepository(db)
    exam_repo = ExamRepository(db)
    
    exam = exam_repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and exam.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    attempts = attempt_repo.list_by_exam(exam_id)
    return [
        {
            "id": a.id,
            "student_id": a.student_id,
            "status": a.status.value,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None
        }
        for a in attempts
    ]

