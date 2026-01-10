from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db
    
    def create_user(self, current_user: User, user_data: UserCreate) -> UserResponse:
        """Create a new user. Only admins can create users."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create users"
            )
        
        # Check if username already exists
        existing = self.user_repo.get_by_username(user_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        password_hash = hash_password(user_data.password)
        user = self.user_repo.create(
            username=user_data.username,
            password_hash=password_hash,
            role=user_data.role,
            email=user_data.email
        )
        
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
        
        return UserResponse.model_validate(user)
    
    def get_user(self, current_user: User, user_id: int) -> UserResponse:
        """Get user by ID. Admins can see any user, others can only see themselves."""
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(user)
    
    def list_users(
        self, 
        current_user: User, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[UserRole] = None,
        sort: Optional[str] = "created_at",
        order: Optional[str] = "desc"
    ) -> tuple[List[UserResponse], int]:
        """List users with sorting and pagination. Only admins can list all users. Returns (users, total_count)."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can list users"
            )
        
        from app.models.user import User as UserModel
        from sqlalchemy import desc, asc
        
        query = self.db.query(UserModel)
        
        # Filter by role
        if role:
            query = query.filter(UserModel.role == role)
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort == "username":
            sort_field = UserModel.username
        elif sort == "created_at":
            sort_field = UserModel.created_at
        else:
            sort_field = UserModel.created_at
        
        if order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        users = query.offset(skip).limit(limit).all()
        return ([UserResponse.model_validate(user) for user in users], total)
    
    def update_user(self, current_user: User, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user. Admins can update any user, others can only update themselves."""
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only admins can change roles
        if user_data.role is not None and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change user roles"
            )
        
        # Only admins can change usernames
        if user_data.username is not None and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change usernames"
            )
        
        # Update fields
        if user_data.username is not None:
            # Validate username is not empty
            if not user_data.username.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username cannot be empty"
                )
            # Check username uniqueness (excluding current user)
            existing_user = self.user_repo.get_by_username(user_data.username.strip())
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            user.username = user_data.username.strip()
        if user_data.email is not None:
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if user_data.email and not re.match(email_pattern, user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            user.email = user_data.email
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.role is not None:
            user.role = user_data.role
        
        self.user_repo.update(user)
        
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
        
        return UserResponse.model_validate(user)
    
    def delete_user(self, current_user: User, user_id: int) -> dict:
        """Delete user. Only admins can delete users."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        # Check if user has active exams or questions that are being used
        if user.role == UserRole.TEACHER:
            # Check if teacher has exams with attempts
            from app.models.exam import Exam
            from app.repositories.attempt_repository import AttemptRepository
            attempt_repo = AttemptRepository(self.db)
            
            teacher_exams = self.db.query(Exam).filter(Exam.owner_id == user.id).all()
            for exam in teacher_exams:
                attempts = attempt_repo.list_by_exam(exam.id)
                if attempts:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot delete user. Teacher has exams with attempts. Please archive or delete exams first."
                    )
        
        # Manually delete related records before deleting user
        # 1. Delete attempts and related data (snapshots, answers, results)
        from app.repositories.attempt_repository import AttemptRepository
        from app.repositories.result_repository import ResultRepository
        from app.models.attempt import AttemptQuestionSnapshot, AttemptAnswer
        
        attempt_repo = AttemptRepository(self.db)
        result_repo = ResultRepository(self.db)
        
        user_attempts = attempt_repo.list_by_student(user.id)
        for attempt in user_attempts:
            # Delete attempt snapshots
            snapshots = self.db.query(AttemptQuestionSnapshot).filter(
                AttemptQuestionSnapshot.attempt_id == attempt.id
            ).all()
            for snapshot in snapshots:
                self.db.delete(snapshot)
            
            # Delete attempt answers
            answers = self.db.query(AttemptAnswer).filter(
                AttemptAnswer.attempt_id == attempt.id
            ).all()
            for answer in answers:
                self.db.delete(answer)
            
            # Delete result if exists
            result = result_repo.get_by_attempt_id(attempt.id)
            if result:
                self.db.delete(result)
            
            # Delete attempt
            self.db.delete(attempt)
        
        # 2. Delete assignments
        from app.repositories.assignment_repository import AssignmentRepository
        assignment_repo = AssignmentRepository(self.db)
        user_assignments = assignment_repo.list_by_student(user.id)
        for assignment in user_assignments:
            self.db.delete(assignment)
        
        # 3. Delete questions (if teacher and not used in exams)
        if user.role == UserRole.TEACHER:
            from app.models.question import Question
            from app.models.exam import ExamQuestion
            
            user_questions = self.db.query(Question).filter(Question.owner_id == user.id).all()
            
            for question in user_questions:
                # Check if question is used in any exams
                exam_questions = self.db.query(ExamQuestion).filter(
                    ExamQuestion.question_id == question.id
                ).all()
                if exam_questions:
                    # Question is used in exams, skip deletion
                    continue
                # Delete question (options and tags will be cascade deleted)
                self.db.delete(question)
        
        # 4. Delete exams (if teacher and no attempts)
        if user.role == UserRole.TEACHER:
            from app.models.exam import Exam, ExamQuestion
            
            user_exams = self.db.query(Exam).filter(Exam.owner_id == user.id).all()
            
            for exam in user_exams:
                # Delete exam questions
                exam_questions = self.db.query(ExamQuestion).filter(
                    ExamQuestion.exam_id == exam.id
                ).all()
                for eq in exam_questions:
                    self.db.delete(eq)
                
                # Delete assignments for this exam
                from app.repositories.assignment_repository import AssignmentRepository
                assignment_repo = AssignmentRepository(self.db)
                exam_assignments = assignment_repo.list_by_exam(exam.id)
                for assignment in exam_assignments:
                    self.db.delete(assignment)
                
                # Delete exam
                self.db.delete(exam)
        
        # 5. Delete audit logs (optional - can keep for history)
        from app.models.audit_log import AuditLog
        audit_logs = self.db.query(AuditLog).filter(AuditLog.actor_id == user.id).all()
        for log in audit_logs:
            self.db.delete(log)
        
        # 6. Finally delete the user
        self.db.delete(user)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
        
        return {"message": "User deleted successfully"}
    
    def activate_user(self, current_user: User, user_id: int) -> UserResponse:
        """Activate a user. Only admins can activate users."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can activate users"
            )
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        self.user_repo.update(user)
        
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
        
        return UserResponse.model_validate(user)
    
    def deactivate_user(self, current_user: User, user_id: int) -> UserResponse:
        """Deactivate a user. Only admins can deactivate users."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can deactivate users"
            )
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deactivating yourself
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        user.is_active = False
        self.user_repo.update(user)
        
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
        
        return UserResponse.model_validate(user)
    
    def change_password(self, current_user: User, old_password: str, new_password: str) -> dict:
        """Change user password. Users can only change their own password."""
        user = self.user_repo.get_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )
        
        # Hash and update password
        user.password_hash = hash_password(new_password)
        self.user_repo.update(user)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")
        
        return {"message": "Password changed successfully"}

