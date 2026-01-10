from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.exam_service import ExamService
from app.schemas.assignment import AssignmentCreate
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamQuestionCreate
from app.schemas.common import PaginatedResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new exam."""
    service = ExamService(db)
    created = service.create_exam(current_user, exam)
    return created


@router.get("/", response_model=PaginatedResponse[ExamResponse])
def list_exams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query("created_at", description="Field to sort by (created_at, name)"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List exams with pagination and sorting."""
    service = ExamService(db)
    skip = (page - 1) * page_size
    exams, total = service.list_exams(current_user, skip, page_size, sort, order)
    return PaginatedResponse.create(exams, total, page, page_size)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get an exam by ID."""
    service = ExamService(db)
    exam = service.get_exam(current_user, exam_id)
    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam: ExamUpdate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update an exam."""
    service = ExamService(db)
    updated = service.update_exam(current_user, exam_id, exam)
    return updated


@router.post("/{exam_id}/questions")
def add_question_to_exam(
    exam_id: int,
    exam_question: ExamQuestionCreate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Add a question to an exam."""
    service = ExamService(db)
    created = service.add_question_to_exam(current_user, exam_id, exam_question)
    return created


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete an exam."""
    service = ExamService(db)
    return service.delete_exam(current_user, exam_id)


@router.delete("/{exam_id}/questions/{question_id}")
def remove_question_from_exam(
    exam_id: int,
    question_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Remove a question from an exam."""
    service = ExamService(db)
    return service.remove_question_from_exam(current_user, exam_id, question_id)


@router.post("/{exam_id}/publish", response_model=ExamResponse)
def publish_exam(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Publish an exam."""
    service = ExamService(db)
    return service.publish_exam(current_user, exam_id)


@router.post("/{exam_id}/unpublish", response_model=ExamResponse)
def unpublish_exam(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Unpublish an exam."""
    service = ExamService(db)
    return service.unpublish_exam(current_user, exam_id)


@router.post("/{exam_id}/archive", response_model=ExamResponse)
def archive_exam(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Archive an exam."""
    service = ExamService(db)
    return service.archive_exam(current_user, exam_id)


@router.get("/{exam_id}/assignments")
def get_exam_assignments(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get assignments for an exam."""
    service = ExamService(db)
    return service.get_exam_assignments(current_user, exam_id)


@router.get("/{exam_id}/statistics")
def get_exam_statistics(
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get statistics for an exam."""
    service = ExamService(db)
    return service.get_exam_statistics(current_user, exam_id)


@router.post("/{exam_id}/assignments/bulk")
def bulk_assign_students(
    exam_id: int,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Bulk assign students to an exam."""
    from app.services.assignment_service import AssignmentService
    service = AssignmentService(db)
    return service.bulk_assign_students(current_user, exam_id, assignment_data.student_ids)

