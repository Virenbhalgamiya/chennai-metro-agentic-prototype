import time
import json
from src.orchestration.state import ComplaintAgentState
from src.services.llm import GroqLLMService
from src.rag.retriever import RAGRetriever
from src.tools.lost_found_tools import LostFoundTools
from src.models.schemas import ResolutionPlan

class ResolutionAgent:
    def __init__(self, llm: GroqLLMService, retriever: RAGRetriever, lf_tools: LostFoundTools):
        self.llm = llm
        self.retriever = retriever
        self.lf_tools = lf_tools

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        
        # RAG Retrieval
        query = f"How to handle {complaint.category.value} regarding: {complaint.normalised_text}"
        retrieved_docs = self.retriever.retrieve(query)
        
        sop_context = "\n".join([f"Source ({d['document_name']}): {d['content']}" for d in retrieved_docs])
        
        # Tools execution
        tool_results = []
        if complaint.category.value == "LOST_FOUND" and complaint.entities and complaint.entities.item_description:
            matches = self.lf_tools.check_lost_found(
                complaint.entities.item_description, 
                complaint.entities.station
            )
            tool_results.append({
                "tool": "check_lost_found",
                "matches": matches
            })
            
        tool_context = json.dumps(tool_results, default=str)
        
        prompt = f"""
        Based on the complaint, the retrieved SOP procedures, and the tool results, recommend the next actions.
        
        Complaint: {complaint.normalised_text}
        Category: {complaint.category.value}
        Severity: {complaint.severity.value}
        Extracted Entities: {complaint.entities.model_dump_json() if complaint.entities else "None"}
        
        SOP Procedures:
        {sop_context}
        
        Tool Results:
        {tool_context}
        
        Generate a structured resolution plan.
        """
        
        result = self.llm.generate_structured(prompt, ResolutionPlan, "You are an operational resolution expert.")
        
        # Enrich the result with actual executed tool data for traceability
        result.tool_results = tool_results
        result.retrieved_sources = list(set([d['document_name'] for d in retrieved_docs]))
        
        complaint.resolution_plan = result
        
        duration = time.time() - start_time
        state["execution_trace"].append({
            "step": "Resolution Agent",
            "input": f"RAG Query: {query}",
            "output": f"Generated {len(result.recommended_actions)} recommended actions.",
            "tool_calls": ["retrieve_sop", "check_lost_found"] if tool_results else ["retrieve_sop"],
            "duration": round(duration, 2)
        })
        
        return state
