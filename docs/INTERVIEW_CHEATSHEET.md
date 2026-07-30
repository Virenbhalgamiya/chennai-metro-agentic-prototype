# INTERVIEW CHEAT SHEET

## PRODUCT PHILOSOPHY
**"Complexity in the backend. Simplicity in the UI."** 
Passengers simply say "what happened", while the AI handles the complex organisational mapping (categorization, severity, officer routing). Staff receive clean, actionable intelligence without needing to debug AI traces.

## THE UX BOUNDARY
1. **Passenger Portal:** Just an intake text box and a list of their own tickets. Statuses are mapped to simple concepts (`Received`, `In progress`, `Information needed`, `Resolved`).
2. **Staff Portal (Nodal Officers):** A case-management dashboard. Officers see extracted entities, AI summaries, and passenger contact info. They click `Approve` or `Escalate`.
3. **Engineering Observability:** RAG vector similarity, LangGraph traces, and JSON tool outputs are stripped from the UI and strictly relegated to backend logging.

## THE AGENTS (Backend Only)
1. **Intake:** Translates and normalizes text.
2. **Triage:** Classifies category (LOST_FOUND, SAFETY) and severity. Output triggers conditional graph edges.
3. **Extraction:** Pulls out specific fields (train number, item description).
4. **Routing:** Uses SQLite tools to find an officer with capacity.
5. **Resolution:** Queries FAISS RAG and tools to recommend actions.
6. **Response:** Drafts the customer reply in the original language.

## AUTHENTICATION & SECURITY
- **RBAC (Role-Based Access Control):** `PASSENGER`, `OFFICER`, `ADMIN`.
- **Ownership:** Database enforces that passengers can only query `WHERE user_id = :id`.
- **Security:** Passwords are hashed using `bcrypt`. Auth credentials and session tokens are **never** injected into LangGraph states or sent to Groq. 

## RAG
- **Why:** To ground resolution recommendations in actual SOPs, preventing hallucinations.
- **Tech:** `BAAI/bge-m3` via `sentence-transformers`. `FAISS` for vector similarity search.

## SAFETY & HUMAN-IN-THE-LOOP
- **Safety Guardrail:** Deterministic Python keyword scanner ("fire", "spark"). Overrides the LLM, sets severity to CRITICAL, and halts the graph for human review.
- **Low Confidence:** If triage certainty is <70%, routes to humans.
