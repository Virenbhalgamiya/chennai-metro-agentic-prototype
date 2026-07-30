# Code Flow

## FLOW A — PASSENGER LOGIN
1. **Passenger Submits Credentials:** User enters email and password on the `login()` screen in `app.py`.
2. **Auth Verification:** Calls `UserRepository.get_by_email()` to fetch the user.
3. **Password Hash Check:** Calls `verify_password()` in `src/services/auth.py` to compare the plaintext input against the bcrypt `password_hash` in SQLite.
4. **Session State:** If valid, `st.session_state["user"]` is populated with `user_id`, `full_name`, and `role`. Streamlit re-renders to show the `passenger_portal()`.

## FLOW B — PASSENGER SUBMITS COMPLAINT
1. **UI Input:** Passenger types into the text box in `passenger_portal()` and clicks Submit.
2. **Pipeline Trigger:** `run_complaint_pipeline(text, user_id)` is called.
3. **Audit & SLA Initiation:** `audit_service.log()` logs the receipt. `sla_service.initialise_sla()` starts the 24-hour countdown.
4. **State Construction:** A `ComplaintAgentState` dictionary is created, embedding a Pydantic `Complaint` object (which notably does **not** contain any passwords or auth tokens).

## FLOW C — AGENTIC PROCESSING
1. **LangGraph Execution:** `graph.invoke(state)` is called.
2. **Intake Node (`src/agents/intake.py`):** Groq detects language and translates to English.
3. **Triage Node (`src/agents/triage.py`):** Groq classifies Category and Severity.
4. **Safety Guardrail (`src/guardrails/safety.py`):** Deterministic Python scans for words like "fire" or "spark". Modifies severity to `CRITICAL` if triggered.
5. **Extraction Node (`src/agents/extraction.py`):** Groq pulls out entities (e.g., station, item).
6. **Routing Node (`src/agents/routing.py`):** Calls `OfficerTools.get_eligible_officers` to query SQLite and assigns an officer based on workload capacity.
7. **Resolution Node (`src/agents/resolution.py`):** Calls `RAGRetriever.retrieve()` to fetch SOPs from FAISS using BGE-M3. Generates a resolution plan.
8. **Response Node (`src/agents/response.py`):** Groq drafts a response in the original language.
9. **Database Persistence:** The final state is written to the `complaints` table via `ComplaintRepository.save()`.

## FLOW D — PASSENGER VIEWS COMPLAINT STATUS
1. **UI Query:** `passenger_portal()` calls `ComplaintRepository.get_by_user_id(st.session_state["user_id"])`.
2. **Status Mapping:** `map_status_for_passenger()` maps complex internal backend statuses (like `AWAITING_REVIEW`) to simple customer statuses (like `In progress`).
3. **Display:** The Streamlit UI renders clean cards for the passenger.

## FLOW E — PASSENGER PROVIDES ADDITIONAL INFORMATION
1. **Information Requested:** If the complaint status is mapped to "Information needed", a text box appears.
2. **Input:** Passenger types additional details.
3. **Database Update:** The text is appended to `original_text`, and `complaint_repo.update_status()` changes it back to `IN_PROGRESS`.

## FLOW F — OFFICER LOGIN
1. Same as Flow A, but `verify_password()` confirms a user with the `OFFICER` role. Streamlit routes them to `staff_portal()`.

## FLOW G — OFFICER OPENS CASE
1. **Dashboard Query:** `staff_portal()` queries `ComplaintRecord` for all cases or cases in `AWAITING_REVIEW` (Human Review tab).
2. **Data Assembly:** The UI pulls the passenger's contact info via `user_repo.get_by_id(c.user_id)`.
3. **Display:** The UI cleanly presents the Passenger Details, Original Complaint, AI Extracted Entities, and the Draft Response.

## FLOW H — OFFICER APPROVES / ESCALATES
1. **Officer Action:** Officer clicks "Approve & Close" or "Escalate".
2. **Database Update:** `complaint_repo.update_status()` updates the case in SQLite.
3. **SLA update:** `sla_service.mark_completed()` stops the timer if approved.
4. **Audit:** `audit_service.log()` permanently records the human's decision.
