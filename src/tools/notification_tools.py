from src.services.notifications import NotificationService

class NotificationTools:
    def __init__(self, service: NotificationService):
        self.service = service

    def notify_customer(self, complaint_id: str) -> bool:
        self.service.notify_customer_acknowledgement(complaint_id)
        return True

    def notify_officer(self, officer_id: str, complaint_id: str) -> bool:
        self.service.notify_officer_assignment(officer_id, complaint_id)
        return True
