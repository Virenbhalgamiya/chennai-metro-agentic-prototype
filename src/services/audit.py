import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.db.repositories import AuditRepository
from src.db.models import AuditEventRecord

class AuditService:
    def __init__(self, repo: AuditRepository):
        self.repo = repo

    def log(
        self,
        complaint_id: str,
        actor_type: str,
        actor_name: str,
        action: str,
        status: str,
        summary: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        record = AuditEventRecord(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            complaint_id=complaint_id,
            actor_type=actor_type,
            actor_name=actor_name,
            action=action,
            status=status,
            summary=summary,
            tool_name=tool_name,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        self.repo.log_event(record)
