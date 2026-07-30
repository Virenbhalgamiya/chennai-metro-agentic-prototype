# Demo Guide (8-10 Minute Script)

## Minute 0-1: Problem and Objective
**Talk track:** "Chennai Metro currently takes 4-5 days to resolve complaints manually because of the overhead of triage, categorization, and routing. This Agentic AI prototype brings that down to under 24 hours. The key product philosophy here is: *Complexity in the backend, simplicity in the UI.* Let me show you."

## Minute 1-3: The Passenger Experience
*Log in as `passenger@demo.com` with `password123`.*
**Talk track:** "Here is the Passenger Portal. Notice how clean it is. We don't ask the passenger to fill out complex dropdowns for 'Category' or 'Severity'. They simply tell us what happened in natural language, in English or Tamil. I'll paste in a complaint about a lost black backpack."
*Submit the 'Lost Backpack' complaint.*
**Talk track:** "The passenger just sees a loading spinner, and then a simple status: *'Received'* or *'In progress'*. They don't need to know what a vector database is."

## Minute 3-6: The Staff Experience
*Log out. Log in as `officer@demo.com` with `password123`.*
**Talk track:** "Now I'm logging into the secure Staff Portal. This is where the AI's heavy lifting is revealed. Instead of raw panicked text, the officer sees a structured case."
*Open the "Human Review" tab. Find the Backpack case.*
**Talk track:** "Look at this case. The AI (LangGraph) has automatically categorized it as `LOST_FOUND`, extracted the route and item description, and checked the SQLite inventory to draft a response. It did all this by pulling the exact Standard Operating Procedure from our FAISS vector database using BGE-M3 embeddings. But importantly, we do not expose those technical traces in this UI—we keep it looking like a real operational product."

## Minute 6-7: Human-in-the-Loop
**Talk track:** "The AI is an assistant, not an autonomous agent that can close tickets. I, as the officer, review the drafted response and click **'Approve & Close'**. Or, if the AI flagged a critical safety hazard (like smoke), I would hit **'Escalate'**."
*Click Approve & Close.*

## Minute 7-8: Full Circle Verification
*Log out. Log in as `passenger@demo.com`.*
**Talk track:** "If I log back in as the passenger, my simple status has seamlessly updated from *'In progress'* to *'Resolved'*, and I can read the final message. The AI abstracted away all the organizational complexity."

## Minute 8-10: Architecture & Security
**Talk track:** "In production, we'd use AWS Cognito for this authentication. The passwords and session tokens are strictly kept out of the LangGraph state and Groq prompts to protect PII. The passenger only sees their own complaints because of strict Row-Level Security and service-layer checks (`WHERE user_id = :id`)."
