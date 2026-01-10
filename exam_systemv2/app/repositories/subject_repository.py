from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.subject import Subject


class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()
    
    def get_by_name(self, name: str) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.name == name).first()
    
    def list_all(self, active_only: bool = True) -> List[Subject]:
        query = self.db.query(Subject)
        if active_only:
            query = query.filter(Subject.is_active == True)
        return query.order_by(Subject.name).all()
    
    def create(self, subject: Subject) -> Subject:
        self.db.add(subject)
        self.db.flush()
        return subject
    
    def update(self, subject: Subject) -> Subject:
        self.db.flush()
        return subject
    
    def delete(self, subject_id: int) -> None:
        subject = self.get_by_id(subject_id)
        if subject:
            self.db.delete(subject)
            self.db.flush()

