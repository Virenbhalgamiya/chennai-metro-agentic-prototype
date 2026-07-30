from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from src.models.enums import ComplaintCategory, Severity, ComplaintSource, CaseStatus, OfficerStatus

class User(BaseModel):
    user_id: str
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    role: str # PASSENGER, OFFICER, ADMIN
    created_at: datetime

class LanguageResult(BaseModel):
    detected_language: str
    normalised_text: str

class TriageResult(BaseModel):
    category: ComplaintCategory
    severity: Severity
    confidence: float
    reasoning_summary: str

class ExtractedEntities(BaseModel):
    station: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    train_id: Optional[str] = None
    coach_id: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    item_description: Optional[str] = None
    item_contents: Optional[List[str]] = None
    person_description: Optional[str] = None
    staff_description: Optional[str] = None
    incident_description: Optional[str] = None
    contact_information: Optional[str] = None
    other_entities: Optional[Dict[str, str]] = None

class RoutingDecision(BaseModel):
    selected_officer_id: Optional[str] = None
    routing_reason: str
    routing_confidence: float
    requires_manual_routing: bool = False

class KnowledgeChunk(BaseModel):
    chunk_id: str
    document_name: str
    content: str
    metadata: Dict[str, Any]

class ResolutionPlan(BaseModel):
    recommended_actions: List[str]
    retrieved_sources: List[str]
    retrieved_context_summary: str
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    requires_investigation: bool
    requires_human_approval: bool
    reasoning_summary: str

class ResponseDraft(BaseModel):
    draft_response: str
    response_language: str
    confidence: float
    requires_approval: bool

class Complaint(BaseModel):
    complaint_id: str
    user_id: Optional[str] = None
    original_text: str
    
    # Metro form fields
    metro_line: Optional[str] = None
    station: Optional[str] = None
    train_id: Optional[str] = None
    incident_time: Optional[str] = None
    
    source: ComplaintSource
    created_at: datetime
    
    # Processed states
    detected_language: Optional[str] = None
    normalised_text: Optional[str] = None
    category: Optional[ComplaintCategory] = None
    severity: Optional[Severity] = None
    safety_flag: bool = False
    requires_human_review: bool = False
    status: CaseStatus = CaseStatus.NEW
    
    entities: Optional[ExtractedEntities] = None
    assigned_officer_id: Optional[str] = None
    routing_reason: Optional[str] = None
    
    resolution_plan: Optional[ResolutionPlan] = None
    draft_response: Optional[str] = None
    closure_otp: Optional[str] = None

class Officer(BaseModel):
    officer_id: str
    name: str
    department: str
    responsibilities: List[ComplaintCategory]
    status: OfficerStatus
    active_case_count: int
    capacity: int

class HumanReview(BaseModel):
    complaint_id: str
    action_taken: str  # APPROVE, EDIT, ESCALATE, RETURN
    edited_response: Optional[str] = None
    notes: Optional[str] = None
    reviewed_at: datetime
    reviewer_id: str

class AuditEvent(BaseModel):
    event_id: str
    timestamp: datetime
    complaint_id: str
    actor_type: str  # AGENT, SYSTEM, HUMAN
    actor_name: str
    action: str
    status: str
    summary: str
    tool_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
