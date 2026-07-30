from typing import Dict, Any, Optional
from src.db.repositories import ComplaintRepository
from src.models.enums import CaseStatus

class CaseTools:
    def __init__(self, repo: ComplaintRepository):
        self.repo = repo

    def get_case(self, complaint_id: str) -> Dict[str, Any]:
        c = self.repo.get_by_id(complaint_id)
        if c:
            return {
                "complaint_id": c.complaint_id,
                "status": c.status,
                "category": c.category,
                "severity": c.severity,
                "assigned_officer_id": c.assigned_officer_id
            }
        return {}

    def update_case_status(self, complaint_id: str, status: str) -> bool:
        try:
            self.repo.update_status(complaint_id, status)
            return True
        except Exception:
            return False
