from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.assignment import Assignment


class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        return self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    def get_by_exam_and_student(self, exam_id: int, student_id: int) -> Optional[Assignment]:
        return self.db.query(Assignment).filter(
            Assignment.exam_id == exam_id,
            Assignment.student_id == student_id
        ).first()
    
    def list_by_student(self, student_id: int) -> List[Assignment]:
        return self.db.query(Assignment).filter(
            Assignment.student_id == student_id
        ).all()
    
    def list_by_exam(self, exam_id: int) -> List[Assignment]:
        return self.db.query(Assignment).filter(
            Assignment.exam_id == exam_id
        ).all()
    
    def create(self, assignment: Assignment) -> Assignment:
        self.db.add(assignment)
        self.db.flush()
        return assignment
    
    def update(self, assignment: Assignment) -> Assignment:
        self.db.flush()
        return assignment

