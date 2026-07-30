import json
from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import OfficerRecord, LostAndFoundItem, ComplaintRecord, AuditEventRecord, SLAStatusRecord, UserRecord
from src.models.schemas import Officer, ComplaintCategory

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_email(self, email: str) -> Optional[UserRecord]:
        return self.db.query(UserRecord).filter(UserRecord.email == email).first()
        
    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        return self.db.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        
    def save(self, record: UserRecord):
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

class OfficerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[OfficerRecord]:
        return self.db.query(OfficerRecord).all()

    def get_by_id(self, officer_id: str) -> Optional[OfficerRecord]:
        return self.db.query(OfficerRecord).filter(OfficerRecord.officer_id == officer_id).first()
        
    def get_eligible_officers(self, category: str) -> List[OfficerRecord]:
        officers = self.db.query(OfficerRecord).filter(OfficerRecord.status == "AVAILABLE").all()
        return [o for o in officers if category in o.responsibilities.split(",")]

    def assign_case(self, officer_id: str) -> bool:
        officer = self.get_by_id(officer_id)
        if officer and officer.active_case_count < officer.capacity:
            officer.active_case_count += 1
            self.db.commit()
            self.db.refresh(officer)
            return True
        return False

class LostAndFoundRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_available_items(self) -> List[LostAndFoundItem]:
        return self.db.query(LostAndFoundItem).filter(LostAndFoundItem.status == "AVAILABLE").all()

class ComplaintRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def save(self, record: ComplaintRecord):
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
        
    def get_by_id(self, complaint_id: str) -> Optional[ComplaintRecord]:
        return self.db.query(ComplaintRecord).filter(ComplaintRecord.complaint_id == complaint_id).first()
        
    def get_by_user_id(self, user_id: str) -> List[ComplaintRecord]:
        return self.db.query(ComplaintRecord).filter(ComplaintRecord.user_id == user_id).order_by(ComplaintRecord.created_at.desc()).all()

    def update_status(self, complaint_id: str, status: str):
        record = self.get_by_id(complaint_id)
        if record:
            record.status = status
            self.db.commit()
            
class AuditRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def log_event(self, record: AuditEventRecord):
        self.db.add(record)
        self.db.commit()
        
    def get_by_complaint(self, complaint_id: str) -> List[AuditEventRecord]:
        return self.db.query(AuditEventRecord).filter(AuditEventRecord.complaint_id == complaint_id).order_by(AuditEventRecord.timestamp).all()
