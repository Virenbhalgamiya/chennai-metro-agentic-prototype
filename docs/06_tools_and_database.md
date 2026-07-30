# Tools and Database

## SQLite - Operational Database
The SQLite database stores the **operational state** of the application.
- **Why?** We need structured relational data for cases, SLA tracking, audit logs, and officer capacity. FAISS cannot handle transactional state or workload math.

### Key Tables
- `complaints`: The main state of the case.
- `officers`: Represents human nodal officers and their active workload capacity.
- `audit_events`: Read-only log of every system and human action.
- `sla_records`: Timestamps and countdowns for the 24-hour SLA.
- `lost_found_inventory`: Mock data representing Chennai Metro's inventory.

## Agents vs. Tools
- **Agent:** An LLM-backed module reasoning about unstructured text.
- **Tool:** A deterministic Python function interacting with the Database or external APIs.

## Key Tools
- **`get_eligible_officers(category)`**: Queries SQLite to find an officer with the right responsibility and available capacity. Called by the Routing Agent. *Why deterministic?* An LLM should never hallucinate officer availability.
- **`check_lost_found(item_desc, station)`**: Queries the SQLite `lost_found_inventory` table for substring matches. Called by the Resolution Agent.
- **`escalate_critical(complaint_id)`**: Called by Streamlit UI when a human escalates, triggering the `NotificationService`.
