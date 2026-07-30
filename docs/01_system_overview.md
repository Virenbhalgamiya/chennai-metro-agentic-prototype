# System Overview

## Separation of Concerns: Passenger vs. Staff

The Chennai Metro Agentic AI prototype enforces a strict boundary between the **Passenger Portal** and the **Staff Portal**, ensuring that complexity remains entirely in the backend.

### 1. The Passenger Experience
The passenger is simply asked: *"What happened?"*
They submit a natural language grievance (in English or Tamil) without needing to understand Metro departments, internal severity scales, or AI confidence scores. 
- The system translates internal states into simple customer-facing statuses: `Received`, `In progress`, `Information needed`, or `Resolved`.
- Passengers can append additional information to their existing case if the system flags it as needed.
- Role-Based Access Control (RBAC) ensures passengers can strictly only view complaints assigned to their own `user_id`.

### 2. The Staff Experience (Nodal Officers)
Officers log into a streamlined operations dashboard where the AI acts as an administrative assistant.
- Instead of raw, panicked text, officers see extracted entities (e.g., Train Route, Item Description), auto-categorized severity, and a drafted response.
- Officers provide **Human-in-the-Loop (HITL)** oversight by clicking `Approve`, `Request Info`, or `Escalate`.
- The dashboard shows real-time officer workload capacities calculated via SQLite transactions.

## End-to-End AI Workflow (Hidden from UI, Kept in Backend)

1. **Intake Agent:** Receives the raw text. It detects the language and produces an English-normalised version, while preserving the original.
2. **Triage Agent:** Uses LLM reasoning to classify the category (e.g., LOST_FOUND) and severity, along with a confidence score.
3. **Safety Guardrail:** A deterministic Python rule engine scans for critical keywords (like "fire" or "spark"). If found, it forces a CRITICAL severity and escalates, overriding the LLM.
4. **Extraction Agent:** Extracts structured entities.
5. **Routing Agent:** Queries the SQLite database to find an available officer matching the category, checking workload capacity.
6. **Resolution Agent (RAG):** Queries the FAISS vector database using BGE-M3 embeddings to retrieve relevant SOPs, and generates a structured resolution plan.
7. **Response Agent:** Drafts a customer-facing response in the passenger's original language.
8. **Human Review:** The workflow pauses, awaiting human officer approval on the Staff Portal.

*(Note: While the AI traces, RAG similarity scores, and FAISS chunks drive the logic, they are intentionally hidden from both passenger and staff UIs to maintain a realistic, user-friendly product feel. This data remains accessible in backend logs for engineering observability.)*
