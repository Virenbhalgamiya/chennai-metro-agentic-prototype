import time
from src.orchestration.state import ComplaintAgentState
from src.services.llm import GroqLLMService
from src.models.schemas import TriageResult
from src.models.enums import CaseStatus

class TriageAgent:
    def __init__(self, llm: GroqLLMService):
        self.llm = llm

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        
        prompt = f"""
        Classify the following complaint.
        Categories: TICKETING_SMART_CARDS, STATION_FACILITIES, TRAIN_OPERATIONS, STAFF_BEHAVIOR, SAFETY_SECURITY, OTHER.
        Severities: LOW, MEDIUM, HIGH, CRITICAL.
        
        Provide your confidence (0.0 to 1.0) in this classification. If the complaint is ambiguous, provide a low confidence score (e.g., < 0.70).
        Also provide a short reasoning summary (max 2 sentences).
        
        Complaint:
        {complaint.normalised_text}
        """
        
        result = self.llm.generate_structured(prompt, TriageResult, "You are a classification assistant for a Metro system.")
        
        complaint.category = result.category
        complaint.severity = result.severity
        
        # Human-in-the-loop logic for ambiguity
        if result.confidence < 0.70:
            complaint.requires_human_review = True
            complaint.status = CaseStatus.HUMAN_TRIAGE
            state["next_node"] = "human_review"
            
        duration = time.time() - start_time
        
        state["execution_trace"].append({
            "step": "Triage Agent",
            "input": complaint.normalised_text[:50] + "...",
            "output": f"Cat: {result.category.value}, Sev: {result.severity.value}, Conf: {result.confidence}",
            "confidence": result.confidence,
            "duration": round(duration, 2)
        })
        
        return state
