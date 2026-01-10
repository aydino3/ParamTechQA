from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.result import Result


class ResultRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_attempt_id(self, attempt_id: int) -> Optional[Result]:
        return self.db.query(Result).filter(Result.attempt_id == attempt_id).first()
    
    def get_by_attempt_ids(self, attempt_ids: List[int]) -> List[Result]:
        """Get results by multiple attempt IDs."""
        if not attempt_ids:
            return []
        return self.db.query(Result).filter(Result.attempt_id.in_(attempt_ids)).all()
    
    def create(self, result: Result) -> Result:
        self.db.add(result)
        self.db.flush()
        return result
    
    def update(self, result: Result) -> Result:
        self.db.flush()
        return result

