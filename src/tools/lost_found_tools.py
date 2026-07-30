from typing import List, Dict, Any
from src.db.repositories import LostAndFoundRepository

class LostFoundTools:
    def __init__(self, repo: LostAndFoundRepository):
        self.repo = repo

    def check_lost_found(self, item_description: str, station: str = None) -> List[Dict[str, Any]]:
        """
        Deterministic tool to check potential items.
        In a real scenario, this would use text search. For prototype, we do simple substring matching.
        """
        items = self.repo.get_available_items()
        matches = []
        desc_lower = item_description.lower() if item_description else ""
        
        for item in items:
            if desc_lower and desc_lower in item.description.lower():
                if station and station.lower() != item.station.lower():
                    continue
                matches.append({
                    "item_id": item.item_id,
                    "description": item.description,
                    "station": item.station,
                    "status": item.status,
                    "notes": item.notes
                })
        return matches
