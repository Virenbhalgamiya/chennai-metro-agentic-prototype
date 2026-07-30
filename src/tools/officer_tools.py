from typing import List, Dict, Any
from src.db.repositories import OfficerRepository
from src.models.schemas import Officer

class OfficerTools:
    def __init__(self, repo: OfficerRepository):
        self.repo = repo

    def get_officers(self) -> List[Dict[str, Any]]:
        officers = self.repo.get_all()
        return [{"officer_id": o.officer_id, "name": o.name, "department": o.department, "status": o.status} for o in officers]

    def get_officer(self, officer_id: str) -> Dict[str, Any]:
        o = self.repo.get_by_id(officer_id)
        if o:
            return {"officer_id": o.officer_id, "name": o.name, "department": o.department, "status": o.status}
        return {}

    def get_eligible_officers(self, category: str) -> List[Dict[str, Any]]:
        officers = self.repo.get_eligible_officers(category)
        return [{"officer_id": o.officer_id, "name": o.name, "capacity": o.capacity, "active": o.active_case_count} for o in officers]

    def get_officer_workload(self, officer_id: str) -> Dict[str, Any]:
        o = self.repo.get_by_id(officer_id)
        if o:
            return {"active_cases": o.active_case_count, "capacity": o.capacity, "available": o.capacity - o.active_case_count}
        return {}

    def assign_officer(self, complaint_id: str, officer_id: str) -> bool:
        # DB side assignment for capacity
        return self.repo.assign_case(officer_id)
