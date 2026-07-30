from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from src.db.database import Base

class UserRecord(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # PASSENGER, OFFICER, ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OfficerRecord(Base):
    __tablename__ = "officers"
    
    officer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    responsibilities = Column(String, nullable=False) # comma separated categories
    status = Column(String, nullable=False)
    active_case_count = Column(Integer, default=0)
    capacity = Column(Integer, default=10)

class ComplaintRecord(Base):
    __tablename__ = "complaints"
    
    complaint_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True) # allow null for legacy
    
    # Metro form fields
    metro_line = Column(String, nullable=True)
    station = Column(String, nullable=True)
    train_id = Column(String, nullable=True)
    incident_time = Column(String, nullable=True)
    
    original_text = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    detected_language = Column(String, nullable=True)
    normalised_text = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    safety_flag = Column(Boolean, default=False)
    requires_human_review = Column(Boolean, default=False)
    status = Column(String, nullable=False, default="NEW")
    
    entities_json = Column(Text, nullable=True)
    assigned_officer_id = Column(String, ForeignKey("officers.officer_id"), nullable=True)
    routing_reason = Column(Text, nullable=True)
    
    resolution_plan_json = Column(Text, nullable=True)
    draft_response = Column(Text, nullable=True)
    closure_otp = Column(String, nullable=True)

class LostAndFoundItem(Base):
    __tablename__ = "lost_found_inventory"
    
    item_id = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=False)
    station = Column(String, nullable=True)
    found_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

class AuditEventRecord(Base):
    __tablename__ = "audit_events"
    
    event_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    complaint_id = Column(String, nullable=False)
    actor_type = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    tool_name = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)

class SLAStatusRecord(Base):
    __tablename__ = "sla_records"
    
    complaint_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True))
    sla_target_at = Column(DateTime(timezone=True))
    elapsed_time_hours = Column(Float, default=0.0)
    remaining_time_hours = Column(Float)
    sla_status = Column(String, nullable=False)
