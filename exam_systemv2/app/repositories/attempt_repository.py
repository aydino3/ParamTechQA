from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.attempt import Attempt, AttemptQuestionSnapshot, AttemptAnswer
from app.models.attempt import AttemptStatus


class AttemptRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, attempt_id: int) -> Optional[Attempt]:
        return self.db.query(Attempt).filter(Attempt.id == attempt_id).first()
    
    def get_active_by_assignment(self, assignment_id: int) -> Optional[Attempt]:
        return self.db.query(Attempt).filter(
            Attempt.assignment_id == assignment_id,
            Attempt.status == AttemptStatus.IN_PROGRESS
        ).first()
    
    def list_by_student(self, student_id: int) -> List[Attempt]:
        return self.db.query(Attempt).filter(
            Attempt.student_id == student_id
        ).all()
    
    def list_by_exam(self, exam_id: int) -> List[Attempt]:
        return self.db.query(Attempt).filter(
            Attempt.exam_id == exam_id
        ).all()
    
    def create(self, attempt: Attempt) -> Attempt:
        self.db.add(attempt)
        self.db.flush()
        return attempt
    
    def update(self, attempt: Attempt) -> Attempt:
        self.db.flush()
        return attempt
    
    def get_snapshots(self, attempt_id: int) -> List[AttemptQuestionSnapshot]:
        return self.db.query(AttemptQuestionSnapshot).filter(
            AttemptQuestionSnapshot.attempt_id == attempt_id
        ).order_by(AttemptQuestionSnapshot.sort_order).all()
    
    def create_snapshot(self, snapshot: AttemptQuestionSnapshot) -> AttemptQuestionSnapshot:
        self.db.add(snapshot)
        self.db.flush()
        return snapshot
    
    def get_answer(self, attempt_id: int, snapshot_id: int) -> Optional[AttemptAnswer]:
        return self.db.query(AttemptAnswer).filter(
            AttemptAnswer.attempt_id == attempt_id,
            AttemptAnswer.snapshot_id == snapshot_id
        ).first()
    
    def create_or_update_answer(self, answer: AttemptAnswer) -> AttemptAnswer:
        existing = self.get_answer(answer.attempt_id, answer.snapshot_id)
        if existing:
            existing.selected_option_json = answer.selected_option_json
            existing.answered_at = answer.answered_at
            self.db.flush()
            return existing
        else:
            self.db.add(answer)
            self.db.flush()
            return answer

