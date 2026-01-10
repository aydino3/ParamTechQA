from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResultResponse(BaseModel):
    id: int
    attempt_id: int
    earned_points: int
    total_points: int
    percentage: int
    released_at: Optional[datetime]
    
    class Config:
        from_attributes = True

