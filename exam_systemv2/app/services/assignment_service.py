from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.user_repository import UserRepository
from app.models.assignment import Assignment, AssignmentStatus
from app.models.user import User, UserRole
from app.schemas.assignment import AssignmentResponse


class AssignmentService:
    def __init__(self, db: Session):
        self.assignment_repo = AssignmentRepository(db)
        self.exam_repo = ExamRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db
    
    def get_assignment(self, current_user: User, assignment_id: int) -> AssignmentResponse:
        """Get assignment by ID. Students can only see their own assignments."""
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Students can only see their own assignments
        if current_user.role == UserRole.STUDENT and assignment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own assignments"
            )
        
        return AssignmentResponse.model_validate(assignment)
    
    def list_assignments(
        self, 
        current_user: User, 
        student_id: Optional[int] = None,
        exam_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[str] = "assigned_at",
        order: Optional[str] = "desc"
    ) -> tuple[List[AssignmentResponse], int]:
        """List assignments with pagination and sorting. Students can only see their own. Returns (assignments, total_count)."""
        from app.models.assignment import Assignment
        from sqlalchemy import desc, asc
        
        query = self.db.query(Assignment)
        
        if current_user.role == UserRole.STUDENT:
            # Students can only see their own assignments
            query = query.filter(Assignment.student_id == current_user.id)
        elif student_id:
            # Teachers/Admins can filter by student
            query = query.filter(Assignment.student_id == student_id)
        elif exam_id:
            # Teachers/Admins can filter by exam
            query = query.filter(Assignment.exam_id == exam_id)
        else:
            # Admins can see all, but we need at least one filter for non-admins
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please specify student_id or exam_id"
                )
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort == "id":
            sort_field = Assignment.id
        elif sort == "assigned_at":
            sort_field = Assignment.assigned_at
        else:
            sort_field = Assignment.assigned_at
        
        if order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        assignments = query.offset(skip).limit(limit).all()
        return ([AssignmentResponse.model_validate(a) for a in assignments], total)
    
    def bulk_assign_students(
        self, 
        current_user: User, 
        exam_id: int, 
        student_ids: List[int]
    ) -> List[AssignmentResponse]:
        """Bulk assign students to an exam. Only teachers/admins can do this."""
        if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can assign students"
            )
        
        exam = self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and exam.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign students to your own exams"
            )
        
        created_assignments = []
        for student_id in student_ids:
            # Check if student exists
            student = self.user_repo.get_by_id(student_id)
            if not student:
                continue  # Skip invalid student IDs
            
            if student.role != UserRole.STUDENT:
                continue  # Skip non-students
            
            # Check if assignment already exists
            existing = self.assignment_repo.get_by_exam_and_student(exam_id, student_id)
            if existing:
                continue  # Skip if already assigned
            
            # Create assignment
            assignment = Assignment(
                exam_id=exam_id,
                student_id=student_id,
                status=AssignmentStatus.ASSIGNED
            )
            assignment = self.assignment_repo.create(assignment)
            created_assignments.append(assignment)
        
        try:
            self.db.commit()
            # Refresh all created assignments
            for assignment in created_assignments:
                self.db.refresh(assignment)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error assigning students: {str(e)}")
        
        return [AssignmentResponse.model_validate(a) for a in created_assignments]
    
    def delete_assignment(self, current_user: User, assignment_id: int) -> dict:
        """Delete an assignment. Only teachers/admins can do this."""
        if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can delete assignments"
            )
        
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        exam = self.exam_repo.get_by_id(assignment.exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Check ownership (unless admin)
        if current_user.role != UserRole.ADMIN and exam.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete assignments for your own exams"
            )
        
        # Check if student has started the exam (has any attempts)
        from app.repositories.attempt_repository import AttemptRepository
        attempt_repo = AttemptRepository(self.db)
        attempts = attempt_repo.list_by_exam(exam.id)
        student_attempts = [a for a in attempts if a.student_id == assignment.student_id]
        
        if student_attempts and len(student_attempts) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete assignment. Student has already started the exam. Please archive the exam instead."
            )
        
        self.db.delete(assignment)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting assignment: {str(e)}")
        
        return {"message": "Assignment deleted successfully"}
