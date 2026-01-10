from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.grading_service import GradingService
from app.schemas.result import ResultResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/{attempt_id}", response_model=ResultResponse)
def get_result(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get result for an attempt."""
    service = GradingService(db)
    result = service.get_result(current_user, attempt_id)
    if not result:
        return {"message": "Result not available"}
    return result


@router.post("/exams/{exam_id}/release")
def release_results(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Release results for an exam."""
    service = GradingService(db)
    service.release_results(current_user, exam_id)
    return {"message": "Results released"}


@router.get("/exams/{exam_id}", response_model=List[dict])
def get_exam_results(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get all results for an exam. Only teachers/admins can access."""
    service = GradingService(db)
    return service.get_exam_results(current_user, exam_id)


@router.get("/exams/{exam_id}/statistics")
def get_exam_statistics(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get statistics for an exam. Only teachers/admins can access."""
    service = GradingService(db)
    return service.get_exam_statistics(current_user, exam_id)


@router.get("/students/{student_id}")
def get_student_results(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all results for a student."""
    service = GradingService(db)
    return service.get_student_results(current_user, student_id)

