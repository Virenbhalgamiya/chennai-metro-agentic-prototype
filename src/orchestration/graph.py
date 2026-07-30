from langgraph.graph import StateGraph, END
import time

from src.orchestration.state import ComplaintAgentState
from src.agents.intake import IntakeAgent
from src.agents.triage import TriageAgent
from src.agents.extraction import ExtractionAgent
from src.agents.routing import RoutingAgent
from src.agents.resolution import ResolutionAgent
from src.agents.response import ResponseAgent
from src.guardrails.safety import SafetyGuardrail
from src.models.enums import Severity, CaseStatus

class GraphBuilder:
    def __init__(
        self, 
        intake_agent: IntakeAgent,
        triage_agent: TriageAgent,
        safety_guardrail: SafetyGuardrail,
        extraction_agent: ExtractionAgent,
        routing_agent: RoutingAgent,
        resolution_agent: ResolutionAgent,
        response_agent: ResponseAgent
    ):
        self.intake_agent = intake_agent
        self.triage_agent = triage_agent
        self.safety_guardrail = safety_guardrail
        self.extraction_agent = extraction_agent
        self.routing_agent = routing_agent
        self.resolution_agent = resolution_agent
        self.response_agent = response_agent
        
    def build(self):
        workflow = StateGraph(ComplaintAgentState)
        
        workflow.add_node("intake", self.intake_node)
        workflow.add_node("triage", self.triage_node)
        workflow.add_node("guardrail", self.guardrail_node)
        workflow.add_node("extraction", self.extraction_node)
        workflow.add_node("routing", self.routing_node)
        workflow.add_node("resolution", self.resolution_node)
        workflow.add_node("response", self.response_node)
        workflow.add_node("human_review", self.human_review_node)
        
        workflow.set_entry_point("intake")
        
        workflow.add_edge("intake", "triage")
        workflow.add_edge("triage", "guardrail")
        
        # Conditional routing after guardrail
        workflow.add_conditional_edges(
            "guardrail",
            self.route_after_guardrail,
            {
                "human_review": "human_review",
                "extraction": "extraction"
            }
        )
        
        workflow.add_edge("extraction", "routing")
        
        # Conditional routing after officer assignment
        workflow.add_conditional_edges(
            "routing",
            self.route_after_routing,
            {
                "human_review": "human_review",
                "resolution": "resolution"
            }
        )
        
        workflow.add_edge("resolution", "response")
        workflow.add_edge("response", "human_review")
        
        workflow.add_edge("human_review", END)
        
        return workflow.compile()

    # Node wrappers
    def intake_node(self, state: ComplaintAgentState):
        return self.intake_agent.process(state)

    def triage_node(self, state: ComplaintAgentState):
        return self.triage_agent.process(state)

    def guardrail_node(self, state: ComplaintAgentState):
        start_time = time.time()
        complaint = state["complaint"]
        
        is_critical, final_severity, reason = self.safety_guardrail.check_safety(
            complaint.normalised_text, complaint.severity
        )
        
        if is_critical:
            complaint.severity = final_severity
            complaint.safety_flag = True
            complaint.requires_human_review = True
            complaint.status = CaseStatus.ESCALATED
            
            state["execution_trace"].append({
                "step": "Safety Guardrail",
                "input": "Checking for critical keywords",
                "output": "CRITICAL OVERRIDE TRIGGERED.",
                "duration": round(time.time() - start_time, 2)
            })
            state["next_node"] = "human_review"
        else:
            state["execution_trace"].append({
                "step": "Safety Guardrail",
                "input": "Checking for critical keywords",
                "output": "Passed.",
                "duration": round(time.time() - start_time, 2)
            })
            state["next_node"] = "extraction"
            
        return state

    def extraction_node(self, state: ComplaintAgentState):
        return self.extraction_agent.process(state)

    def routing_node(self, state: ComplaintAgentState):
        return self.routing_agent.process(state)

    def resolution_node(self, state: ComplaintAgentState):
        return self.resolution_agent.process(state)

    def response_node(self, state: ComplaintAgentState):
        return self.response_agent.process(state)

    def human_review_node(self, state: ComplaintAgentState):
        # This node acts as a sink in the graph representing the handoff to Streamlit UI.
        complaint = state["complaint"]
        if complaint.status not in [CaseStatus.ESCALATED, CaseStatus.HUMAN_TRIAGE]:
            complaint.status = CaseStatus.AWAITING_REVIEW
        state["execution_trace"].append({
            "step": "Human Review Handoff",
            "input": "Graph execution completed.",
            "output": f"State set to {complaint.status.value}. Waiting for UI action.",
            "duration": 0.0
        })
        return state

    # Edge logic
    def route_after_guardrail(self, state: ComplaintAgentState):
        complaint = state["complaint"]
        # If triage marked it low confidence or guardrail marked it critical
        if complaint.requires_human_review and state.get("next_node") == "human_review":
            return "human_review"
        return "extraction"

    def route_after_routing(self, state: ComplaintAgentState):
        complaint = state["complaint"]
        if complaint.requires_human_review: # Routing failed to find officer
            return "human_review"
        return "resolution"
