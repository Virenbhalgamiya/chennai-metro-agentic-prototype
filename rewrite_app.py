import os

NEW_APP_PY = """import streamlit as st
import uuid
import json
from datetime import datetime, timezone

from src.db.database import SessionLocal
from src.db.seed import seed_db
from src.db.repositories import OfficerRepository, ComplaintRepository, LostAndFoundRepository, AuditRepository, UserRepository
from src.db.models import UserRecord
from src.services.auth import verify_password, hash_password
from src.services.llm import GroqLLMService
from src.services.sla import SLAService
from src.services.audit import AuditService
from src.services.notifications import NotificationService
from src.services.otp import OTPService
from src.rag.retriever import RAGRetriever
from src.tools.officer_tools import OfficerTools
from src.tools.lost_found_tools import LostFoundTools
from src.tools.case_tools import CaseTools
from src.tools.notification_tools import NotificationTools
from src.tools.escalation_tools import EscalationTools
from src.guardrails.safety import SafetyGuardrail
from src.agents.intake import IntakeAgent
from src.agents.triage import TriageAgent
from src.agents.extraction import ExtractionAgent
from src.agents.routing import RoutingAgent
from src.agents.resolution import ResolutionAgent
from src.agents.response import ResponseAgent
from src.orchestration.graph import GraphBuilder
from src.orchestration.state import ComplaintAgentState
from src.models.schemas import Complaint
from src.models.enums import ComplaintSource, CaseStatus
from src.db.models import ComplaintRecord, SLAStatusRecord

st.set_page_config(page_title="Chennai Metro Services", layout="wide")

@st.cache_resource
def init_system():
    seed_db()
    llm = GroqLLMService()
    retriever = RAGRetriever()
    retriever.initialize()
    return llm, retriever

llm, retriever = init_system()

db = SessionLocal()
user_repo = UserRepository(db)
officer_repo = OfficerRepository(db)
complaint_repo = ComplaintRepository(db)
lf_repo = LostAndFoundRepository(db)
audit_repo = AuditRepository(db)

sla_service = SLAService(db)
audit_service = AuditService(audit_repo)
notif_service = NotificationService()

officer_tools = OfficerTools(officer_repo)
lf_tools = LostFoundTools(lf_repo)
case_tools = CaseTools(complaint_repo)
notif_tools = NotificationTools(notif_service)
escalation_tools = EscalationTools(notif_service, complaint_repo)
safety_guardrail = SafetyGuardrail()

intake_agent = IntakeAgent(llm)
triage_agent = TriageAgent(llm)
extraction_agent = ExtractionAgent(llm)
routing_agent = RoutingAgent(officer_tools)
resolution_agent = ResolutionAgent(llm, retriever, lf_tools)
response_agent = ResponseAgent(llm)

graph = GraphBuilder(
    intake_agent, triage_agent, safety_guardrail, extraction_agent, 
    routing_agent, resolution_agent, response_agent
).build()

def map_status_for_passenger(internal_status: str) -> str:
    if internal_status in [CaseStatus.NEW.value, "INTAKE_COMPLETE", "TRIAGE_COMPLETE", "ROUTING_PENDING"]:
        return "Received"
    elif internal_status in [CaseStatus.IN_PROGRESS.value, "ASSIGNED", "INVESTIGATING", CaseStatus.ESCALATED.value, "RESPONSE_PENDING", CaseStatus.AWAITING_REVIEW.value, CaseStatus.HUMAN_TRIAGE.value, "AWAITING_ADMIN_INFO"]:
        return "In progress"
    elif internal_status == "WAITING_FOR_PASSENGER":
        return "Information needed"
    elif internal_status in [CaseStatus.RESOLVED.value, CaseStatus.CLOSED.value]:
        return "Resolved"
    return "In progress"

def run_complaint_pipeline(original_text: str, user_id: str, rigid_data: dict):
    comp_id = f"CMP-{uuid.uuid4().hex[:8].upper()}"
    complaint = Complaint(
        complaint_id=comp_id,
        user_id=user_id,
        original_text=original_text,
        pnr_number=rigid_data.get("pnr_number"),
        train_details=rigid_data.get("train_details"),
        stations_info=rigid_data.get("stations_info"),
        date_time_info=rigid_data.get("date_time_info"),
        class_quota=rigid_data.get("class_quota"),
        allocation=rigid_data.get("allocation"),
        source=ComplaintSource.WEB,
        created_at=datetime.now(timezone.utc)
    )
    
    state: ComplaintAgentState = {
        "complaint": complaint,
        "execution_trace": [],
        "next_node": "",
        "error": None
    }
    
    audit_service.log(comp_id, "SYSTEM", "Streamlit", "SUBMITTED", "SUCCESS", "Complaint received.")
    sla_service.initialise_sla(comp_id, complaint.created_at)
    
    with st.spinner("Processing AI pipeline..."):
        try:
            final_state = graph.invoke(state)
        except Exception as e:
            import traceback
            traceback.print_exc()
            st.error(f"System processing failed. Error: {e}")
            return None
            
    final_complaint = final_state["complaint"]
    
    record = ComplaintRecord(
        complaint_id=final_complaint.complaint_id,
        user_id=final_complaint.user_id,
        original_text=final_complaint.original_text,
        pnr_number=final_complaint.pnr_number,
        train_details=final_complaint.train_details,
        stations_info=final_complaint.stations_info,
        date_time_info=final_complaint.date_time_info,
        class_quota=final_complaint.class_quota,
        allocation=final_complaint.allocation,
        source=final_complaint.source.value,
        created_at=final_complaint.created_at,
        detected_language=final_complaint.detected_language,
        normalised_text=final_complaint.normalised_text,
        category=final_complaint.category.value if final_complaint.category else None,
        severity=final_complaint.severity.value if final_complaint.severity else None,
        safety_flag=final_complaint.safety_flag,
        requires_human_review=final_complaint.requires_human_review,
        status=final_complaint.status.value,
        entities_json=final_complaint.entities.model_dump_json() if final_complaint.entities else None,
        assigned_officer_id=final_complaint.assigned_officer_id,
        routing_reason=final_complaint.routing_reason,
        resolution_plan_json=final_complaint.resolution_plan.model_dump_json() if final_complaint.resolution_plan else None,
        draft_response=final_complaint.draft_response
    )
    
    try:
        complaint_repo.save(record)
        audit_service.log(comp_id, "SYSTEM", "LangGraph", "PROCESSED", "SUCCESS", "Pipeline completed.")
        return final_complaint
    except Exception as e:
        st.error(f"Save Failed.")
        return None

if "user" not in st.session_state:
    st.session_state["user"] = None

def login_register():
    st.title("🚇 Chennai Metro Sign In")
    tab1, tab2 = st.tabs(["Log In", "Register (New User)"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Log In", type="primary"):
            user = user_repo.get_by_email(email.strip())
            if user and verify_password(password, user.password_hash):
                st.session_state["user"] = {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "role": user.role,
                    "phone": user.phone
                }
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
        st.divider()
        st.info("Demo Accounts:\n- Passenger: passenger@demo.com / password123\n- Officer: officer@demo.com / password123\n- Admin: admin@demo.com / password123")

    with tab2:
        st.subheader("Passenger Registration")
        r_name = st.text_input("Full Name")
        r_phone = st.text_input("Phone Number (e.g. 6357013746)")
        r_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        r_age = st.number_input("Age", min_value=1, max_value=120, value=30)
        r_email = st.text_input("Email ID")
        r_pass = st.text_input("Password", type="password")
        
        if st.button("Register", type="primary"):
            if r_name and r_phone and r_email and r_pass:
                existing = user_repo.get_by_email(r_email.strip())
                if existing:
                    st.error("Email already registered.")
                else:
                    new_user = UserRecord(
                        user_id=f"USR-{uuid.uuid4().hex[:6].upper()}",
                        full_name=r_name,
                        phone=r_phone,
                        email=r_email.strip(),
                        gender=r_gender,
                        age=r_age,
                        password_hash=hash_password(r_pass),
                        role="PASSENGER"
                    )
                    user_repo.save(new_user)
                    st.success("Registration successful! Please log in.")
            else:
                st.warning("Please fill all fields.")

def logout():
    st.session_state["user"] = None
    if "selected_case" in st.session_state:
        del st.session_state["selected_case"]
    st.rerun()

def passenger_portal():
    st.sidebar.title(f"Hello, {st.session_state['user']['full_name']}")
    if st.sidebar.button("Log Out"):
        logout()
        
    st.title("Chennai Metro Help & Grievance")
    
    if "selected_case" in st.session_state:
        case_id = st.session_state["selected_case"]
        c = complaint_repo.get_by_id(case_id)
        if c and c.user_id == st.session_state["user"]["user_id"]:
            if st.button("← Your complaints"):
                del st.session_state["selected_case"]
                st.rerun()
            
            st.subheader(c.original_text[:50] + "...")
            st.caption(f"Submitted {c.created_at.strftime('%d %b, %I:%M %p')}")
            
            status = map_status_for_passenger(c.status)
            st.write(f"**Status:** {status}")
            
            st.markdown("### Latest update")
            if c.draft_response and c.status in [CaseStatus.RESOLVED.value, CaseStatus.CLOSED.value]:
                st.info(c.draft_response)
            else:
                st.info("We're looking into your complaint. We'll update you here when there's progress.")
                
            st.markdown("### Your complaint")
            st.write(f"> {c.original_text}")
            
            if status == "Information needed":
                st.markdown("### We need a little more information")
                add_info = st.text_area("Please provide additional details:")
                if st.button("Send"):
                    c.original_text += f"\\n\\n[Additional Info]: {add_info}"
                    complaint_repo.update_status(c.complaint_id, CaseStatus.AWAITING_REVIEW.value)
                    st.success("Information submitted.")
                    st.rerun()
        else:
            del st.session_state["selected_case"]
            st.rerun()
    else:
        st.subheader("Submit a New Complaint")
        st.write("Please provide your travel and incident details.")
        
        with st.form("complaint_form"):
            col1, col2 = st.columns(2)
            pnr = col1.text_input("PNR Number")
            train = col2.text_input("Train Number & Name")
            
            st.markdown("**Stations**")
            scol1, scol2, scol3, scol4 = st.columns(4)
            s_from = scol1.text_input("From")
            s_to = scol2.text_input("To")
            s_board = scol3.text_input("Boarding")
            s_res = scol4.text_input("Reserved Upto")
            
            st.markdown("**Date & Time**")
            dcol1, dcol2, dcol3 = st.columns(3)
            date_dep = dcol1.date_input("Departure Date")
            time_dep = dcol2.time_input("Departure Time")
            time_arr = dcol3.time_input("Arrival Time")
            
            st.markdown("**Class & Quota**")
            qcol1, qcol2 = st.columns(2)
            c_class = qcol1.selectbox("Class", ["Sleeper", "3AC", "2AC", "1AC", "General"])
            c_quota = qcol2.selectbox("Quota", ["General", "Tatkal", "Ladies", "Senior Citizen"])
            
            st.markdown("**Allocation**")
            acol1, acol2 = st.columns(2)
            coach = acol1.text_input("Coach Number (e.g. S3, B1)")
            berth = acol2.text_input("Berth / Seat Number")
            
            st.markdown("**Incident Description**")
            desc = st.text_area("What happened?")
            
            submitted = st.form_submit_button("Submit Complaint")
            
            if submitted:
                if not desc.strip():
                    st.warning("Incident description is required.")
                else:
                    rigid_data = {
                        "pnr_number": pnr,
                        "train_details": train,
                        "stations_info": f"From: {s_from}, To: {s_to}, Board: {s_board}, Res: {s_res}",
                        "date_time_info": f"Dep: {date_dep} {time_dep}, Arr: {time_arr}",
                        "class_quota": f"{c_class} / {c_quota}",
                        "allocation": f"Coach: {coach}, Berth: {berth}"
                    }
                    
                    full_text = f"[Train: {train} | PNR: {pnr} | Coach: {coach} | Berth: {berth}] - {desc}"
                    
                    c = run_complaint_pipeline(full_text, st.session_state["user"]["user_id"], rigid_data)
                    if c:
                        st.success("Your complaint has been submitted.")
                        
        st.divider()
        st.subheader("Your complaints")
        cases = complaint_repo.get_by_user_id(st.session_state["user"]["user_id"])
        if cases:
            for c in cases:
                with st.container(border=True):
                    st.markdown(f"**{c.original_text[:60]}...**")
                    st.write(f"{map_status_for_passenger(c.status)} • {c.created_at.strftime('%d %b, %I:%M %p')}")
                    if st.button("Open", key=f"open_{c.complaint_id}"):
                        st.session_state["selected_case"] = c.complaint_id
                        st.rerun()
        else:
            st.write("No complaints found.")

def staff_portal():
    st.sidebar.title(f"Staff: {st.session_state['user']['full_name']}")
    st.sidebar.write(f"Role: {st.session_state['user']['role']}")
    if st.sidebar.button("Log Out"):
        logout()
        
    tabs = ["Cases", "Human Review", "Officers"]
    if st.session_state["user"]["role"] == "ADMIN":
        tabs.append("Admin (Info Requests)")
        tabs.append("Knowledge Base (RAG)")
        
    selected_tab = st.tabs(tabs)
    
    with selected_tab[0]:
        st.header("Operations: Cases Dashboard")
        cases = db.query(ComplaintRecord).order_by(ComplaintRecord.created_at.desc()).limit(20).all()
        if cases:
            for c in cases:
                with st.expander(f"{c.complaint_id} - {c.category} ({c.status})"):
                    st.write(f"**Preview:** {c.original_text[:100]}...")
                    passenger = user_repo.get_by_id(c.user_id) if c.user_id else None
                    if passenger:
                        st.write(f"**Passenger:** {passenger.full_name} | {passenger.phone} | {passenger.email}")
                    st.write(f"**PNR/Train:** {c.pnr_number} / {c.train_details}")
                    st.write(f"**Allocation:** {c.allocation}")
                    st.write(f"**Assigned:** {c.assigned_officer_id}")
        else:
            st.info("No cases yet.")
            
    with selected_tab[1]:
        st.header("Human-in-the-loop Review")
        cases_for_review = db.query(ComplaintRecord).filter(
            ComplaintRecord.status.in_([CaseStatus.AWAITING_REVIEW.value, CaseStatus.ESCALATED.value, CaseStatus.HUMAN_TRIAGE.value])
        ).all()
        
        if cases_for_review:
            for c in cases_for_review:
                with st.container(border=True):
                    st.subheader(f"Case: {c.complaint_id}")
                    
                    passenger = user_repo.get_by_id(c.user_id) if c.user_id else None
                    if passenger:
                        st.markdown("**Passenger Details:**")
                        st.write(f"{passenger.full_name} | Phone: {passenger.phone} | Age: {passenger.age} | Gender: {passenger.gender}")
                    
                    st.markdown("**Railway Details:**")
                    rcol1, rcol2, rcol3 = st.columns(3)
                    rcol1.write(f"PNR: {c.pnr_number}")
                    rcol1.write(f"Train: {c.train_details}")
                    rcol2.write(f"Allocation: {c.allocation}")
                    rcol2.write(f"Class: {c.class_quota}")
                    rcol3.write(f"Stations: {c.stations_info}")
                    
                    st.markdown("**Complaint:**")
                    st.info(c.original_text)
                    
                    if c.draft_response:
                        st.markdown("**Draft Response:**")
                        st.success(c.draft_response)
                        
                    # OTP State Management per case
                    otp_key = f"otp_sent_{c.complaint_id}"
                    if otp_key not in st.session_state:
                        st.session_state[otp_key] = False
                        
                    if st.session_state[otp_key]:
                        # Verification form
                        entered_otp = st.text_input("Enter OTP provided by Passenger:", key=f"otp_in_{c.complaint_id}")
                        if st.button("Verify & Close Case", key=f"verify_{c.complaint_id}"):
                            # DB check
                            if entered_otp and entered_otp == c.closure_otp:
                                complaint_repo.update_status(c.complaint_id, CaseStatus.CLOSED.value)
                                sla_service.mark_completed(c.complaint_id)
                                audit_service.log(c.complaint_id, "HUMAN", st.session_state["user"]["full_name"], "APPROVED_AND_CLOSED", "SUCCESS", "OTP verified.")
                                st.session_state[otp_key] = False
                                st.success("OTP Verified. Case Closed.")
                                st.rerun()
                            else:
                                st.error("Invalid OTP.")
                    else:
                        ca, cb, cc = st.columns(3)
                        if ca.button("Send OTP & Close", key=f"app_{c.complaint_id}"):
                            otp = OTPService.generate_otp()
                            c.closure_otp = otp
                            db.commit()
                            if passenger and passenger.phone:
                                OTPService.send_otp(passenger.phone, otp)
                            st.session_state[otp_key] = True
                            st.rerun()
                            
                        if cb.button("Request Info (Route to Admin)", key=f"edit_{c.complaint_id}"):
                            complaint_repo.update_status(c.complaint_id, "AWAITING_ADMIN_INFO")
                            audit_service.log(c.complaint_id, "HUMAN", st.session_state["user"]["full_name"], "REQUEST_INFO", "SUCCESS", "Routed to Admin.")
                            st.rerun()
                            
                        if cc.button("Escalate", key=f"esc_{c.complaint_id}"):
                            escalation_tools.escalate_critical(c.complaint_id)
                            st.rerun()
        else:
            st.success("No cases waiting for human review.")
            
    with selected_tab[2]:
        st.header("Nodal Officers")
        officers = officer_repo.get_all()
        for o in officers:
            st.write(f"**{o.name}** ({o.department}) - Load: {o.active_case_count}/{o.capacity}")
            st.divider()
            
    if st.session_state["user"]["role"] == "ADMIN":
        with selected_tab[3]:
            st.header("Admin: Information Requests")
            admin_cases = db.query(ComplaintRecord).filter_by(status="AWAITING_ADMIN_INFO").all()
            if admin_cases:
                for ac in admin_cases:
                    with st.container(border=True):
                        st.write(f"**Case:** {ac.complaint_id}")
                        p = user_repo.get_by_id(ac.user_id)
                        if p:
                            st.write(f"Passenger: {p.full_name} | {p.phone}")
                        st.info(ac.original_text)
                        if st.button("Mark Info Gathered (Return to Officer)", key=f"ret_{ac.complaint_id}"):
                            complaint_repo.update_status(ac.complaint_id, CaseStatus.AWAITING_REVIEW.value)
                            st.rerun()
            else:
                st.success("No pending information requests.")
                
        with selected_tab[4]:
            st.header("Knowledge Base Admin")
            query = st.text_input("Search SOPs")
            if st.button("Search") and query:
                res = retriever.retrieve(query)
                for r in res:
                    st.subheader(r['document_name'])
                    st.write(r['content'])
                    st.divider()

if not st.session_state["user"]:
    login_register()
else:
    role = st.session_state["user"]["role"]
    if role == "PASSENGER":
        passenger_portal()
    else:
        staff_portal()
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(NEW_APP_PY)
print("app.py rewritten successfully.")
