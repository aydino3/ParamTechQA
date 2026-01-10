from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.audit_log import AuditLog
import json


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        actor_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        self.db.add(log)
        self.db.flush()
        return log

