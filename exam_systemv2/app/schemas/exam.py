from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.exam import ExamStatus, GradingPolicy


class ExamQuestionCreate(BaseModel):
    question_id: int
    sort_order: int
    points: int


class ExamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    attempts_allowed: int = 1
    shuffle_questions: bool = False
    shuffle_options: bool = False
    grading_policy: GradingPolicy
    pass_score: Optional[int] = None


class ExamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    attempts_allowed: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    grading_policy: Optional[GradingPolicy] = None
    pass_score: Optional[int] = None
    status: Optional[ExamStatus] = None


class ExamQuestionResponse(BaseModel):
    id: int
    question_id: int
    sort_order: int
    points: int
    
    class Config:
        from_attributes = True


class ExamResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    duration_minutes: int
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    attempts_allowed: int
    shuffle_questions: bool
    shuffle_options: bool
    grading_policy: GradingPolicy
    pass_score: Optional[int]
    status: ExamStatus
    created_at: datetime
    exam_questions: List[ExamQuestionResponse] = []
    
    class Config:
        from_attributes = True

