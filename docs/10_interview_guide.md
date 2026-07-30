# Interview Guide

## Top Questions and Answers

**Q: Why don't passengers choose complaint categories on the intake form?**
A: Classification is an internal organisational concern. Expecting a panicked passenger to know the difference between a "Technical Issue" and a "Safety Hazard" adds cognitive friction and leads to miscategorization. The core product philosophy is *Complexity in the backend, simplicity in the UI*. We let the passenger speak naturally, and rely on the AI (Triage Agent) to map it to our internal ontologies.

**Q: Why separate passenger and staff portals?**
A: To enforce Role-Based Access Control (RBAC) and adhere to the principle of least privilege. Passengers should only see simple, consumer-friendly statuses (e.g., "Received", "Resolved") and only access their own data. Staff need operational visibility (e.g., "HUMAN_TRIAGE", "ESCALATED", Officer capacity). Mixing these UIs risks leaking PII or internal processes.

**Q: How is complaint ownership enforced?**
A: Ownership is enforced at the database and repository layer, not just by hiding UI elements. The `ComplaintRecord` in SQLite has a foreign key to `user_id`. When a passenger logs in, the `ComplaintRepository` specifically queries `SELECT * FROM complaints WHERE user_id = :id`.

**Q: Why does the officer see passenger contact information?**
A: If a case requires physical follow-up (e.g., returning a lost laptop), the officer needs to contact the passenger. However, we do not build complex Twilio call-tracking into this dashboard—we simply surface the `phone` and `email` to the authorised staff member so they can reach out via standard channels.

**Q: Why doesn't the LLM receive authentication credentials?**
A: Security and PII protection. Passwords, hashes, and session tokens are strictly handled by the Auth layer (bcrypt). They are never injected into the `ComplaintAgentState` or passed to Groq, ensuring that if the LLM prompts are ever logged or intercepted, sensitive authentication material is safe.

**Q: Why isn't Agent Trace shown in the UI?**
A: Because this is a product, not an engineering playground. Exposing raw JSON, FAISS similarity scores, and LangGraph node transitions clutters the interface and confuses non-technical Metro Staff. The AI trace data is preserved in backend audit logs for observability and debugging by engineers, but kept off the main UI.

**Q: Why are internal statuses mapped to simpler customer statuses?**
A: A passenger doesn't care if their ticket is in `ROUTING_PENDING` or `HUMAN_TRIAGE`. They only care if it's `Received`, `In progress`, `Information needed`, or `Resolved`. Internal statuses dictate backend LangGraph logic; external statuses manage customer expectations.

**Q: How do same-user duplicates differ from cross-user incident reports?**
A: If a single passenger submits 5 tickets about their lost bag, that is a *same-user duplicate* and should be merged to prevent spam. However, if 5 *different* passengers report that "Coach 3 has no AC", that is not a duplicate—it is a *cross-user incident*. We must preserve all 5 complaints to track the impact of the incident, while linking them to a single operational ticket for the technical officer.
