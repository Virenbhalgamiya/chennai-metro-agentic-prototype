import time
from src.orchestration.state import ComplaintAgentState
from src.services.llm import GroqLLMService
from src.models.schemas import ExtractedEntities

class ExtractionAgent:
    def __init__(self, llm: GroqLLMService):
        self.llm = llm

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        
        prompt = f"""
        Extract relevant entities from this complaint based on its category ({complaint.category.value}).
        Do NOT hallucinate information. If information is not present, leave it as null.
        
        Complaint:
        {complaint.normalised_text}
        """
        
        result = self.llm.generate_structured(prompt, ExtractedEntities, "You are a precise data extraction assistant.")
        complaint.entities = result
        
        duration = time.time() - start_time
        
        state["execution_trace"].append({
            "step": "Extraction Agent",
            "input": f"Extract for {complaint.category.value}",
            "output": "Entities extracted.",
            "duration": round(duration, 2)
        })
        
        return state
