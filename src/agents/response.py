import time
from src.orchestration.state import ComplaintAgentState
from src.services.llm import GroqLLMService
from src.models.schemas import ResponseDraft

class ResponseAgent:
    def __init__(self, llm: GroqLLMService):
        self.llm = llm

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        plan = complaint.resolution_plan
        
        actions_str = "\n".join(plan.recommended_actions) if plan else "Under investigation."
        
        prompt = f"""
        Draft a customer-facing response for this complaint. 
        IMPORTANT: 
        1. Write the response in the original language of the complaint ({complaint.detected_language}).
        2. Do not claim something is resolved unless it is verified.
        3. Be polite and professional.
        
        Original Complaint: {complaint.original_text}
        Normalised Complaint: {complaint.normalised_text}
        Category: {complaint.category.value}
        Recommended Internal Actions: {actions_str}
        """
        
        result = self.llm.generate_structured(prompt, ResponseDraft, "You are a customer service response drafter.")
        
        complaint.draft_response = result.draft_response
        
        duration = time.time() - start_time
        state["execution_trace"].append({
            "step": "Response Agent",
            "input": "Drafting response based on resolution plan.",
            "output": f"Drafted in {result.response_language}.",
            "duration": round(duration, 2)
        })
        
        return state
