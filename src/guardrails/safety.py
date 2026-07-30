from typing import Tuple
from src.models.enums import Severity

class SafetyGuardrail:
    CRITICAL_KEYWORDS = {
        "fire", "smoke", "bomb", "weapon", "violence", "threat", 
        "electrical hazard", "medical emergency", "severe injury",
        "spark", "sparks", "தீ", "புகை", "வெடிகுண்டு", "ஆயுதம்", "வன்முறை", "அச்சுறுத்தல்", "மருத்துவ அவசரம்"
    }

    def check_safety(self, text: str, current_severity: Severity) -> Tuple[bool, Severity, str]:
        text_lower = text.lower()
        for kw in self.CRITICAL_KEYWORDS:
            if kw in text_lower:
                return (
                    True, 
                    Severity.CRITICAL, 
                    f"Deterministic safety override triggered by keyword: '{kw}'"
                )
        return (False, current_severity, "No critical safety keywords detected.")
