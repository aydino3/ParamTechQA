from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.question import QuestionType


class QuestionOptionCreate(BaseModel):
    text: str
    is_correct: bool


class QuestionOptionResponse(BaseModel):
    id: int
    text: str
    is_correct: bool
    
    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    title: str
    body: str
    difficulty: int = Field(ge=1, le=5, description="Difficulty level must be between 1 and 5")
    type: QuestionType
    explanation: Optional[str] = None
    options: List[QuestionOptionCreate]
    tags: List[str] = []


class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, description="Title cannot be empty if provided")
    body: Optional[str] = Field(default=None, min_length=1, description="Body cannot be empty if provided")
    difficulty: Optional[int] = Field(default=None, ge=1, le=5, description="Difficulty level must be between 1 and 5")
    explanation: Optional[str] = None
    options: Optional[List[QuestionOptionCreate]] = None
    tags: Optional[List[str]] = None


class QuestionResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    body: str
    difficulty: int
    type: QuestionType
    explanation: Optional[str]
    created_at: datetime
    updated_at: datetime
    options: List[QuestionOptionResponse]
    tags: List[str]
    
    class Config:
        from_attributes = True

