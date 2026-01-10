from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.question_service import QuestionService
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.schemas.common import PaginatedResponse
from app.core.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new question."""
    service = QuestionService(db)
    created = service.create_question(current_user, question)
    return created


@router.get("/", response_model=PaginatedResponse[QuestionResponse])
def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    type: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("created_at", description="Field to sort by (created_at, title, difficulty)"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List questions with optional filtering, pagination, and sorting."""
    service = QuestionService(db)
    
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    skip = (page - 1) * page_size
    
    questions, total = service.list_questions(
        current_user, 
        skip, 
        page_size,
        search=search,
        tags=tag_list,
        difficulty=difficulty,
        type=type,
        owner_id=owner_id,
        sort=sort,
        order=order
    )
    
    return PaginatedResponse.create(questions, total, page, page_size)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get a question by ID."""
    service = QuestionService(db)
    question = service.get_question(current_user, question_id)
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question: QuestionUpdate,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update a question."""
    service = QuestionService(db)
    updated = service.update_question(current_user, question_id, question)
    return updated


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a question."""
    service = QuestionService(db)
    service.delete_question(current_user, question_id)
    return {"message": "Question deleted"}

