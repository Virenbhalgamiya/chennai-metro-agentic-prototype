from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.db.models import SLAStatusRecord
from src.models.enums import SLAStatus

class SLAService:
    def __init__(self, db: Session):
        self.db = db
        self.target_hours = 24.0

    def initialise_sla(self, complaint_id: str, created_at: datetime):
        if not created_at.tzinfo:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        target_at = created_at + timedelta(hours=self.target_hours)
        
        record = SLAStatusRecord(
            complaint_id=complaint_id,
            created_at=created_at,
            sla_target_at=target_at,
            elapsed_time_hours=0.0,
            remaining_time_hours=self.target_hours,
            sla_status=SLAStatus.ON_TRACK.value
        )
        self.db.add(record)
        self.db.commit()

    def update_sla(self, complaint_id: str) -> SLAStatusRecord:
        record = self.db.query(SLAStatusRecord).filter_by(complaint_id=complaint_id).first()
        if not record:
            return None
            
        now = datetime.now(timezone.utc)
        created_at = record.created_at
        if not created_at.tzinfo:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        elapsed = (now - created_at).total_seconds() / 3600.0
        remaining = self.target_hours - elapsed
        
        record.elapsed_time_hours = elapsed
        record.remaining_time_hours = remaining
        
        if record.sla_status == SLAStatus.COMPLETED.value:
            pass # Already completed
        elif elapsed > self.target_hours:
            record.sla_status = SLAStatus.BREACHED.value
        elif elapsed > 16.0:
            record.sla_status = SLAStatus.AT_RISK.value
        else:
            record.sla_status = SLAStatus.ON_TRACK.value
            
        self.db.commit()
        return record

    def mark_completed(self, complaint_id: str):
        record = self.update_sla(complaint_id)
        if record:
            record.sla_status = SLAStatus.COMPLETED.value
            self.db.commit()
