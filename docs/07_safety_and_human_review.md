# Safety and Human Review

## Why Safety cannot rely solely on LLMs
LLMs can occasionally hallucinate or fail to understand the severity of physical real-world hazards (like electrical fires). We must not let a model mistakenly classify a "bomb" threat as "LOW" severity. 

## Deterministic Guardrail
`src/guardrails/safety.py` scans the normalised text against a hardcoded list of critical keywords (e.g., "fire", "smoke", "weapon"). If triggered, it overrides the LLM's severity to `CRITICAL` and forcefully routes the graph to the `human_review` node, skipping normal processing.

## Human-in-the-Loop Thresholds
Humans intervene in three scenarios:
1. **Critical Escalation:** The safety guardrail triggers.
2. **Ambiguous Triage:** The Triage Agent's confidence is `< 0.70`.
3. **Final Approval:** The Response Agent drafts a message, but a nodal officer must click "Approve" on the Streamlit UI before it's "sent".

## No Hallucinated Claims
The Resolution and Response agents are strictly prompted to **never** claim an item is found or a repair is complete unless verified by a tool. 
- *BAD:* "Your laptop bag has been found."
- *GOOD:* "A potentially matching item has been identified and is awaiting verification."
