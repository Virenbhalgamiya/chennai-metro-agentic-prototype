import time
from src.orchestration.state import ComplaintAgentState
from src.tools.officer_tools import OfficerTools
from src.models.schemas import RoutingDecision

class RoutingAgent:
    def __init__(self, tools: OfficerTools):
        self.tools = tools

    def process(self, state: ComplaintAgentState) -> ComplaintAgentState:
        start_time = time.time()
        complaint = state["complaint"]
        category = complaint.category.value
        
        # Deterministic routing based on available officers and capacity
        eligible_officers = self.tools.get_eligible_officers(category)
        
        if not eligible_officers:
            complaint.requires_human_review = True
            complaint.routing_reason = f"No eligible/available officer found for category {category}."
            state["execution_trace"].append({
                "step": "Routing Agent",
                "input": f"Category: {category}",
                "output": "Manual routing required.",
                "duration": round(time.time() - start_time, 2)
            })
            return state

        # Pick officer with most available capacity
        selected = max(eligible_officers, key=lambda x: x["capacity"] - x["active"])
        
        # Attempt assignment in DB
        success = self.tools.assign_officer(complaint.complaint_id, selected["officer_id"])
        
        if success:
            complaint.assigned_officer_id = selected["officer_id"]
            complaint.routing_reason = f"Assigned to {selected['name']} based on category and capacity."
            
            state["execution_trace"].append({
                "step": "Routing Agent",
                "input": f"Category: {category}",
                "output": f"Routed to {selected['officer_id']}",
                "tool_calls": ["get_eligible_officers", "assign_officer"],
                "duration": round(time.time() - start_time, 2)
            })
        else:
            complaint.requires_human_review = True
            complaint.routing_reason = "Assignment failed at DB level."
            
        return state
