from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.repositories.teacher_profile_repository import TeacherProfileRepository
from app.repositories.subject_repository import SubjectRepository
from app.models.user import User, UserRole
from app.models.teacher_profile import TeacherProfile
from app.models.subject import Subject
from app.schemas.teacher_profile import TeacherProfileCreate, TeacherProfileUpdate, TeacherProfileResponse
from app.schemas.subject import SubjectResponse


class TeacherProfileService:
    def __init__(self, db: Session):
        self.profile_repo = TeacherProfileRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.db = db
    
    def get_profile(self, teacher: User) -> TeacherProfileResponse:
        """Get teacher profile. Teachers can only see their own profile."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can access their profile"
            )
        
        profile = self.profile_repo.get_by_user_id(teacher.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Load subjects relationship
        self.db.refresh(profile)
        return TeacherProfileResponse.model_validate(profile)
    
    def create_or_update_profile(self, teacher: User, data: TeacherProfileCreate) -> TeacherProfileResponse:
        """Create or update teacher profile. Teachers can only update their own profile."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create/update their profile"
            )
        
        # Auto-extract first_name and last_name from username if not provided
        first_name = data.first_name
        last_name = data.last_name
        
        if not first_name or not last_name:
            # Extract from username: "firstname.lastname" or "firstname_lastname" or just "firstname"
            username_parts = teacher.username.replace('_', '.').split('.')
            if not first_name and len(username_parts) >= 1:
                first_name = username_parts[0].capitalize()
            if not last_name and len(username_parts) >= 2:
                last_name = username_parts[-1].capitalize()
            elif not last_name:
                last_name = ""  # Allow empty last name if can't extract
        
        # Check if profile exists
        profile = self.profile_repo.get_by_user_id(teacher.id)
        
        if profile:
            # Update existing profile
            profile.first_name = first_name
            profile.last_name = last_name
            profile.bio = data.bio
            profile.phone = data.phone
            
            # Update subjects
            self._update_teacher_subjects(profile, data.subject_ids)
            
            profile = self.profile_repo.update(profile)
        else:
            # Create new profile
            profile = TeacherProfile(
                user_id=teacher.id,
                first_name=first_name,
                last_name=last_name,
                bio=data.bio,
                phone=data.phone
            )
            profile = self.profile_repo.create(profile)
            
            # Add subjects
            self._update_teacher_subjects(profile, data.subject_ids)
        
        try:
            self.db.commit()
            self.db.refresh(profile)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")
        
        return TeacherProfileResponse.model_validate(profile)
    
    def update_profile(self, teacher: User, data: TeacherProfileUpdate) -> TeacherProfileResponse:
        """Update teacher profile with optional fields."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can update their profile"
            )
        
        profile = self.profile_repo.get_by_user_id(teacher.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Auto-extract first_name and last_name from username if not provided
        first_name = data.first_name
        last_name = data.last_name
        
        if first_name is None or last_name is None:
            # Extract from username: "firstname.lastname" or "firstname_lastname" or just "firstname"
            username_parts = teacher.username.replace('_', '.').split('.')
            if first_name is None and len(username_parts) >= 1:
                first_name = username_parts[0].capitalize()
            if last_name is None and len(username_parts) >= 2:
                last_name = username_parts[-1].capitalize()
            elif last_name is None:
                last_name = profile.last_name if profile.last_name else ""  # Keep existing or empty
        
        # Update fields if provided
        if first_name is not None:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if data.bio is not None:
            profile.bio = data.bio
        if data.phone is not None:
            profile.phone = data.phone
        
        # Update subjects if provided
        if data.subject_ids is not None:
            self._update_teacher_subjects(profile, data.subject_ids)
        
        profile = self.profile_repo.update(profile)
        
        try:
            self.db.commit()
            self.db.refresh(profile)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")
        
        return TeacherProfileResponse.model_validate(profile)
    
    def _update_teacher_subjects(self, profile: TeacherProfile, subject_ids: List[int]) -> None:
        """Update teacher's subjects by replacing existing ones."""
        # Validate all subject IDs exist
        for subject_id in subject_ids:
            subject = self.subject_repo.get_by_id(subject_id)
            if not subject:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject with ID {subject_id} not found"
                )
            if not subject.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject '{subject.name}' is not active"
                )
        
        # Clear existing subjects
        profile.subjects.clear()
        
        # Add new subjects
        for subject_id in subject_ids:
            subject = self.subject_repo.get_by_id(subject_id)
            profile.subjects.append(subject)
    
    def add_subject_to_teacher(self, teacher: User, subject_id: int) -> None:
        """Add a subject to teacher's profile."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can manage their subjects"
            )
        
        profile = self.profile_repo.get_by_user_id(teacher.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        if subject not in profile.subjects:
            profile.subjects.append(subject)
            self.profile_repo.update(profile)
            
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=f"Error adding subject: {str(e)}")
    
    def remove_subject_from_teacher(self, teacher: User, subject_id: int) -> None:
        """Remove a subject from teacher's profile."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can manage their subjects"
            )
        
        profile = self.profile_repo.get_by_user_id(teacher.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        if subject in profile.subjects:
            profile.subjects.remove(subject)
            self.profile_repo.update(profile)
            
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=f"Error removing subject: {str(e)}")
    
    def get_teacher_subjects(self, teacher: User) -> List[SubjectResponse]:
        """Get all subjects for a teacher."""
        if teacher.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can access their subjects"
            )
        
        profile = self.profile_repo.get_by_user_id(teacher.id)
        if not profile:
            return []
        
        self.db.refresh(profile)
        return [SubjectResponse.model_validate(subject) for subject in profile.subjects]

