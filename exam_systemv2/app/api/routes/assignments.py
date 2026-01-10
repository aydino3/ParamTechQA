from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.assignment_service import AssignmentService
from app.schemas.assignment import AssignmentResponse, AssignmentCreate
from app.schemas.common import PaginatedResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AssignmentResponse])
def list_assignments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    exam_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("assigned_at", description="Field to sort by (assigned_at, id)"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List assignments with pagination and sorting. Students can only see their own assignments."""
    service = AssignmentService(db)
    skip = (page - 1) * page_size
    assignments, total = service.list_assignments(
        current_user, 
        student_id, 
        exam_id,
        skip,
        page_size,
        sort,
        order
    )
    return PaginatedResponse.create(assignments, total, page, page_size)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignment by ID. Students can only see their own assignments."""
    service = AssignmentService(db)
    return service.get_assignment(current_user, assignment_id)


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete an assignment. Only teachers/admins can do this."""
    service = AssignmentService(db)
    return service.delete_assignment(current_user, assignment_id)

