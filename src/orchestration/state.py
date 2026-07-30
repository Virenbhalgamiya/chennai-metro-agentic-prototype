from typing import TypedDict, Optional, List, Dict, Any
from src.models.schemas import Complaint, ExtractedEntities, ResolutionPlan

class ComplaintAgentState(TypedDict):
    complaint: Complaint
    
    # Execution tracing for UI/Audit
    execution_trace: List[Dict[str, Any]]
    
    # To handle routing logic
    next_node: str
    error: Optional[str]
