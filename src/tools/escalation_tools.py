from src.services.notifications import NotificationService
from src.db.repositories import ComplaintRepository
from src.models.enums import CaseStatus

class EscalationTools:
    def __init__(self, notif_service: NotificationService, repo: ComplaintRepository):
        self.notif_service = notif_service
        self.repo = repo

    def escalate_critical(self, complaint_id: str) -> bool:
        try:
            self.notif_service.notify_critical_escalation(complaint_id)
            self.repo.update_status(complaint_id, CaseStatus.ESCALATED.value)
            return True
        except Exception:
            return False
