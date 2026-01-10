from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.question import Question, QuestionOption, QuestionTag


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, question_id: int) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def list_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        return self.db.query(Question).filter(
            Question.owner_id == owner_id
        ).offset(skip).limit(limit).all()
    
    def create(self, question: Question) -> Question:
        self.db.add(question)
        self.db.flush()
        return question
    
    def update(self, question: Question) -> Question:
        self.db.flush()
        return question
    
    def delete(self, question: Question):
        self.db.delete(question)
        self.db.flush()
    
    def get_options(self, question_id: int) -> List[QuestionOption]:
        return self.db.query(QuestionOption).filter(
            QuestionOption.question_id == question_id
        ).all()
    
    def get_tags(self, question_id: int) -> List[QuestionTag]:
        return self.db.query(QuestionTag).filter(
            QuestionTag.question_id == question_id
        ).all()

