from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.subject import SubjectResponse


class TeacherProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class TeacherProfileCreate(TeacherProfileBase):
    subject_ids: List[int] = []


class TeacherProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    subject_ids: Optional[List[int]] = None


class TeacherProfileResponse(TeacherProfileBase):
    id: int
    user_id: int
    subjects: List[SubjectResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

