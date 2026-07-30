# LangGraph Orchestration

## Why LangGraph?
Instead of a normal Python script (e.g., `agent1()`, `agent2()`), LangGraph provides a robust state-machine. It allows us to manage execution state explicitly, implement conditional logic (routing critical cases directly to human review), and provides an execution trace for observability.

## State
The graph state (`ComplaintAgentState`) is a `TypedDict` containing the core `Complaint` Pydantic model, an `execution_trace` array, and metadata for edge routing (`next_node`).

## Nodes and Edges
| Node | Purpose | Reads | Writes | Next Nodes |
|---|---|---|---|---|
| intake | Lang/Translate | raw_text | language, normalised_text | triage |
| triage | Categorize | normalised_text | category, severity, status | guardrail |
| guardrail | Safety Override | normalised_text | severity, safety_flag | extraction OR human_review |
| extraction | Find Entities | normalised_text | entities | routing |
| routing | Assign Officer | category | assigned_officer_id | resolution OR human_review |
| resolution | RAG & Action | entities, SOPs | resolution_plan | response |
| response | Draft Msg | plan, language | draft_response | human_review |
| human_review | Pause & Wait | status | (Waits for UI) | END |

## Conditional Paths
- **Critical Path:** If the guardrail triggers, the edge function `route_after_guardrail` skips extraction, routing, and resolution, sending the case straight to `human_review` with `ESCALATED` status.
- **Low Confidence Path:** If triage confidence is < 0.70, it routes to `human_review` with `HUMAN_TRIAGE` status.
