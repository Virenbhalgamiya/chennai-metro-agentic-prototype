import random
import logging

logger = logging.getLogger(__name__)

class OTPService:
    @staticmethod
    def generate_otp() -> str:
        """Generates a 6-digit OTP."""
        return str(random.randint(100000, 999999))
        
    @staticmethod
    def send_otp(phone_number: str, otp: str):
        """
        Simulates sending an OTP via SMS.
        In a production environment, this would integrate with Twilio or AWS SNS.
        """
        # For prototype testing, we'll log it out clearly and return it so it can be shown in the UI for ease of demoing.
        print(f"\n==========================================")
        print(f"SMS SENT TO {phone_number}")
        print(f"Your Chennai Metro Case Closure OTP is: {otp}")
        print(f"==========================================\n")
        logger.info(f"OTP {otp} sent to {phone_number}")
        return True
