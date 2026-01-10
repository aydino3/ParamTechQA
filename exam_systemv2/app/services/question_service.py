from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.repositories.question_repository import QuestionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.question import Question, QuestionOption, QuestionTag
from app.models.user import User, UserRole
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:
    def __init__(self, db: Session):
        self.question_repo = QuestionRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db
    
    def create_question(self, owner: User, data: QuestionCreate) -> Question:
        """Create a new question with options and tags."""
        # Validate: Difficulty must be between 1 and 5
        if not (1 <= data.difficulty <= 5):
            raise HTTPException(
                status_code=400, 
                detail="Difficulty level must be between 1 and 5"
            )
        
        # Validate: At least one option must be correct
        if not any(opt.is_correct for opt in data.options):
            raise HTTPException(status_code=400, detail="At least one option must be marked as correct")
        
        # Validate: Multiple choice questions need at least 2 options
        if data.type.value == "multiple_choice" and len(data.options) < 2:
            raise HTTPException(status_code=400, detail="Multiple choice questions must have at least 2 options")
        
        # Validate: True/False questions need exactly 2 options
        if data.type.value == "true_false" and len(data.options) != 2:
            raise HTTPException(status_code=400, detail="True/False questions must have exactly 2 options")
        
        question = Question(
            owner_id=owner.id,
            title=data.title,
            body=data.body,
            difficulty=data.difficulty,
            type=data.type,
            explanation=data.explanation
        )
        question = self.question_repo.create(question)
        
        # Add options
        for opt_data in data.options:
            option = QuestionOption(
                question_id=question.id,
                text=opt_data.text,
                is_correct=1 if opt_data.is_correct else 0
            )
            self.db.add(option)
        
        # Add tags
        for tag_name in data.tags:
            tag = QuestionTag(question_id=question.id, tag=tag_name)
            self.db.add(tag)
        
        # Create audit log
        self.audit_repo.create(
            actor_id=owner.id,
            action="question_create",
            entity_type="question",
            entity_id=question.id
        )
        
        # Single commit for all changes
        try:
            self.db.commit()
            self.db.refresh(question)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating question: {str(e)}")
        
        return question
    
    def update_question(self, owner: User, question_id: int, data: QuestionUpdate) -> Question:
        """Update an existing question."""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if question.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if data.title is not None:
            # Validate: Title cannot be empty
            if not data.title.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Title cannot be empty"
                )
            question.title = data.title
        if data.body is not None:
            # Validate: Body cannot be empty
            if not data.body.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Body cannot be empty"
                )
            question.body = data.body
        if data.difficulty is not None:
            # Validate: Difficulty must be between 1 and 5
            if not (1 <= data.difficulty <= 5):
                raise HTTPException(
                    status_code=400,
                    detail="Difficulty level must be between 1 and 5"
                )
            question.difficulty = data.difficulty
        if data.explanation is not None:
            question.explanation = data.explanation
        
        if data.options is not None:
            # Validate: At least one option must be correct
            if not any(opt.is_correct for opt in data.options):
                raise HTTPException(status_code=400, detail="At least one option must be marked as correct")
            
            # Validate: Multiple choice questions need at least 2 options
            if question.type.value == "multiple_choice" and len(data.options) < 2:
                raise HTTPException(status_code=400, detail="Multiple choice questions must have at least 2 options")
            
            # Validate: True/False questions need exactly 2 options
            if question.type.value == "true_false" and len(data.options) != 2:
                raise HTTPException(status_code=400, detail="True/False questions must have exactly 2 options")
            
            # Remove old options
            for opt in question.options:
                self.db.delete(opt)
            # Add new options
            for opt_data in data.options:
                option = QuestionOption(
                    question_id=question.id,
                    text=opt_data.text,
                    is_correct=1 if opt_data.is_correct else 0
                )
                self.db.add(option)
        
        if data.tags is not None:
            # Remove old tags
            for tag in question.tags:
                self.db.delete(tag)
            # Add new tags
            for tag_name in data.tags:
                tag = QuestionTag(question_id=question.id, tag=tag_name)
                self.db.add(tag)
        
        self.question_repo.update(question)
        
        try:
            self.db.commit()
            self.db.refresh(question)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating question: {str(e)}")
        
        return question
    
    def delete_question(self, owner: User, question_id: int):
        """Delete a question."""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if question.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if question is used in any exams
        from app.models.exam import ExamQuestion
        exam_questions = self.db.query(ExamQuestion).filter(ExamQuestion.question_id == question_id).all()
        if exam_questions:
            exam_ids = [eq.exam_id for eq in exam_questions]
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete question. It is used in {len(exam_questions)} exam(s). Please remove it from exams first."
            )
        
        self.question_repo.delete(question)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting question: {str(e)}")
    
    def list_questions(
        self, 
        owner: User, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[int] = None,
        type: Optional[str] = None,
        owner_id: Optional[int] = None,
        sort: Optional[str] = "created_at",
        order: Optional[str] = "desc"
    ) -> tuple[List[Question], int]:
        """List questions with optional filtering, sorting, and pagination. Returns (questions, total_count)."""
        from sqlalchemy import func, distinct
        
        # Base query
        query = self.db.query(Question)
        
        # Filter by owner (unless admin or specific owner_id requested)
        if owner.role.value != "admin":
            if owner_id and owner_id != owner.id:
                # Non-admins can't see other users' questions
                return ([], 0)
            query = query.filter(Question.owner_id == owner.id)
        elif owner_id:
            query = query.filter(Question.owner_id == owner_id)
        
        # Search in title and body
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Question.title.ilike(search_term),
                    Question.body.ilike(search_term)
                )
            )
        
        # Filter by difficulty
        if difficulty is not None:
            query = query.filter(Question.difficulty == difficulty)
        
        # Filter by type
        if type:
            query = query.filter(Question.type == type)
        
        # Filter by tags (use distinct to avoid duplicates from join)
        if tags:
            from app.models.question import QuestionTag
            query = query.join(QuestionTag).filter(QuestionTag.tag.in_(tags)).distinct()
        
        # Get total count before pagination
        total = query.count()
        
        # Sorting
        if sort == "title":
            sort_field = Question.title
        elif sort == "difficulty":
            sort_field = Question.difficulty
        elif sort == "created_at":
            sort_field = Question.created_at
        else:
            sort_field = Question.created_at
        
        if order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        # Pagination
        questions = query.offset(skip).limit(limit).all()
        
        return (questions, total)
    
    def get_question(self, owner: User, question_id: int) -> Question:
        """Get a question by ID."""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if question.owner_id != owner.id and owner.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return question

