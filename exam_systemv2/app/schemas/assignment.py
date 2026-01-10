from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.assignment import AssignmentStatus


class AssignmentCreate(BaseModel):
    exam_id: int
    student_ids: List[int]


class AssignmentResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    status: AssignmentStatus
    assigned_at: datetime
    
    class Config:
        from_attributes = True

