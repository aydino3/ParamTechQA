from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.teacher_profile import TeacherProfile


class TeacherProfileRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_id(self, user_id: int) -> Optional[TeacherProfile]:
        return self.db.query(TeacherProfile).filter(TeacherProfile.user_id == user_id).first()
    
    def get_by_id(self, profile_id: int) -> Optional[TeacherProfile]:
        return self.db.query(TeacherProfile).filter(TeacherProfile.id == profile_id).first()
    
    def create(self, profile: TeacherProfile) -> TeacherProfile:
        self.db.add(profile)
        self.db.flush()
        return profile
    
    def update(self, profile: TeacherProfile) -> TeacherProfile:
        self.db.flush()
        return profile
    
    def list_all(self) -> List[TeacherProfile]:
        return self.db.query(TeacherProfile).all()

