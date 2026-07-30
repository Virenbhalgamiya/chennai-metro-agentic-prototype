import time
from src.orchestration.state import ComplaintAgentState
from src.services.llm import GroqLLMService
from src.models.schemas import LanguageResult

class IntakeAgent:
    def __init__(self, llm: GroqLLMService):
        self.llm = llm

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        
        prompt = f"""
        Analyze the following complaint text.
        1. Detect the language.
        2. If it is not English, translate it accurately to English (normalised_text).
        3. If it is already English, provide a clean normalised version of it.
        
        Complaint:
        {complaint.original_text}
        """
        
        result = self.llm.generate_structured(prompt, LanguageResult, "You are a precise translation and intake assistant.")
        
        complaint.detected_language = result.detected_language
        complaint.normalised_text = result.normalised_text
        
        duration = time.time() - start_time
        
        state["execution_trace"].append({
            "step": "Intake Agent",
            "input": complaint.original_text[:50] + "...",
            "output": f"Language: {result.detected_language}",
            "duration": round(duration, 2)
        })
        
        return state
