import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def send_notification(self, recipient: str, template: str, context: dict):
        """Simulates sending a notification (SMS/Email)."""
        logger.info(f"SIMULATED NOTIFICATION to {recipient}: [{template}] {context}")
        return True

    def notify_customer_acknowledgement(self, complaint_id: str, phone: str = "demo-customer"):
        self.send_notification(phone, "ACKNOWLEDGEMENT", {"complaint_id": complaint_id})

    def notify_officer_assignment(self, officer_id: str, complaint_id: str):
        self.send_notification(officer_id, "NEW_ASSIGNMENT", {"complaint_id": complaint_id})

    def notify_critical_escalation(self, complaint_id: str):
        self.send_notification("SAFETY_TEAM", "CRITICAL_ESCALATION", {"complaint_id": complaint_id})
