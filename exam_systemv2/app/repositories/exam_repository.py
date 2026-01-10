from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.exam import Exam, ExamQuestion
from app.models.exam import ExamStatus


class ExamRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, exam_id: int) -> Optional[Exam]:
        return self.db.query(Exam).filter(Exam.id == exam_id).first()
    
    def list_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Exam]:
        return self.db.query(Exam).filter(
            Exam.owner_id == owner_id
        ).offset(skip).limit(limit).all()
    
    def list_published(self) -> List[Exam]:
        return self.db.query(Exam).filter(
            Exam.status == ExamStatus.PUBLISHED
        ).all()
    
    def create(self, exam: Exam) -> Exam:
        self.db.add(exam)
        self.db.flush()
        return exam
    
    def update(self, exam: Exam) -> Exam:
        self.db.flush()
        return exam
    
    def get_exam_questions(self, exam_id: int) -> List[ExamQuestion]:
        return self.db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == exam_id
        ).order_by(ExamQuestion.sort_order).all()
    
    def add_exam_question(self, exam_question: ExamQuestion) -> ExamQuestion:
        self.db.add(exam_question)
        self.db.flush()
        return exam_question
    
    def remove_exam_question(self, exam_question: ExamQuestion):
        self.db.delete(exam_question)
        self.db.flush()

