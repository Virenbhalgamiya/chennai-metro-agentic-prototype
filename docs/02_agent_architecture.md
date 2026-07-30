# Agent Architecture

The prototype uses a multi-agent architecture where distinct Python classes backed by Groq handle specialized tasks.

## Why Multiple Agents?
Instead of a single massive prompt, breaking tasks down (Intake -> Triage -> Extraction -> Resolution -> Response) reduces hallucination, simplifies debugging, enables structured Pydantic outputs per stage, and allows conditional graph routing (e.g., skipping extraction if the safety guardrail triggers).

## Agents

### 1. Intake Agent
- **Purpose:** Language detection and translation.
- **Input:** Raw complaint text.
- **Output:** `LanguageResult` (detected language, English normalisation).

### 2. Triage Agent
- **Purpose:** Categorisation and severity assessment.
- **Input:** Normalised text.
- **Output:** `TriageResult` (category, severity, confidence).
- **Human Involvement:** If confidence is low, sets status to `HUMAN_TRIAGE` to pause the graph.

### 3. Extraction Agent
- **Purpose:** Extract entities like "train_id" or "item_description".
- **Input:** Normalised text, Category.
- **Output:** `ExtractedEntities`.

### 4. Routing Agent
- **Purpose:** Assign an officer.
- **Why it's an Agent:** It bridges the AI state with the deterministic DB tools. It reads the category, uses `OfficerTools` to query SQLite, and assigns the best officer based on capacity.

### 5. Resolution Agent
- **Purpose:** Recommend actions based on RAG.
- **Input:** Extracted entities, Category, SOPs (from FAISS), Tool results.
- **Output:** `ResolutionPlan` (actions, reasoning).

### 6. Response Agent
- **Purpose:** Draft the customer response.
- **Input:** Resolution plan, detected language.
- **Output:** `ResponseDraft`.

## Why Nodal Officers are NOT Agents
The 5 nodal officers represent **actual human beings** in the Chennai Metro organisation. They are modeled as database records in SQLite, not as AI instances. Their purpose is to review the AI's work and approve real-world actions.
