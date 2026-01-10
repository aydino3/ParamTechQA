from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.attempt import AttemptStatus


class AttemptStartResponse(BaseModel):
    attempt_id: int
    started_at: datetime
    ends_at: datetime
    questions: List[Dict[str, Any]]


class AnswerSubmit(BaseModel):
    snapshot_id: int
    selected_option: Any  # Can be string, int, or dict


class AttemptQuestionSnapshotResponse(BaseModel):
    id: int
    snapshot_id: int
    sort_order: int
    points: int
    question_title: str
    question_body: str
    options: List[Dict[str, Any]]
    answer: Optional[Any] = None
    
    class Config:
        from_attributes = True


class AttemptResponse(BaseModel):
    id: int
    exam_id: int
    attempt_no: int
    started_at: datetime
    ends_at: datetime
    submitted_at: Optional[datetime]
    status: AttemptStatus
    
    class Config:
        from_attributes = True

