import pytest
from src.guardrails.safety import SafetyGuardrail
from src.models.enums import Severity

def test_safety_guardrail_critical_keyword():
    guardrail = SafetyGuardrail()
    text = "There is smoke coming from the train"
    
    is_critical, final_severity, reason = guardrail.check_safety(text, Severity.LOW)
    
    assert is_critical is True
    assert final_severity == Severity.CRITICAL
    assert "smoke" in reason

def test_safety_guardrail_safe_text():
    guardrail = SafetyGuardrail()
    text = "I lost my bag at the station"
    
    is_critical, final_severity, reason = guardrail.check_safety(text, Severity.MEDIUM)
    
    assert is_critical is False
    assert final_severity == Severity.MEDIUM
