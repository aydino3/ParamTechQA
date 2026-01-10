from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.repositories.subject_repository import SubjectRepository
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse


class SubjectService:
    def __init__(self, db: Session):
        self.subject_repo = SubjectRepository(db)
        self.db = db
    
    def create_subject(self, admin: User, data: SubjectCreate) -> SubjectResponse:
        """Create a new subject. Only admins can create subjects."""
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create subjects"
            )
        
        # Check if name already exists
        existing = self.subject_repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject name already exists"
            )
        
        subject = Subject(
            name=data.name,
            description=data.description,
            is_active=data.is_active
        )
        subject = self.subject_repo.create(subject)
        
        try:
            self.db.commit()
            self.db.refresh(subject)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating subject: {str(e)}")
        
        return SubjectResponse.model_validate(subject)
    
    def update_subject(self, admin: User, subject_id: int, data: SubjectUpdate) -> SubjectResponse:
        """Update a subject. Only admins can update subjects."""
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update subjects"
            )
        
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check if new name already exists (if name is being updated)
        if data.name and data.name != subject.name:
            existing = self.subject_repo.get_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subject name already exists"
                )
            subject.name = data.name
        
        if data.description is not None:
            subject.description = data.description
        if data.is_active is not None:
            subject.is_active = data.is_active
        
        subject = self.subject_repo.update(subject)
        
        try:
            self.db.commit()
            self.db.refresh(subject)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating subject: {str(e)}")
        
        return SubjectResponse.model_validate(subject)
    
    def delete_subject(self, admin: User, subject_id: int) -> None:
        """Delete a subject. Only admins can delete subjects."""
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete subjects"
            )
        
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        self.subject_repo.delete(subject_id)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting subject: {str(e)}")
    
    def get_subject(self, subject_id: int) -> SubjectResponse:
        """Get a subject by ID."""
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        return SubjectResponse.model_validate(subject)
    
    def list_subjects(self, active_only: bool = True) -> List[SubjectResponse]:
        """List all subjects."""
        subjects = self.subject_repo.list_all(active_only=active_only)
        return [SubjectResponse.model_validate(subject) for subject in subjects]

