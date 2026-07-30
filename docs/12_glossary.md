# Glossary

- **Agent:** An LLM-backed module designed to perform reasoning over text and output structured data.
- **Tool:** A deterministic function (often database CRUD or API calls) invoked by an agent to fetch facts or perform actions.
- **LangGraph:** A library for building stateful, multi-actor applications with LLMs, modeled as graphs (nodes and edges).
- **State:** A shared data structure (like a dictionary) that passes through LangGraph nodes, mutating as it goes.
- **RAG (Retrieval-Augmented Generation):** Fetching external documents (like SOPs) to provide factual context to an LLM before it answers.
- **Embeddings:** Converting text into arrays of numbers (vectors) so computers can calculate semantic similarity.
- **FAISS:** Facebook AI Similarity Search. A library for efficient similarity search of dense vectors.
- **BGE-M3:** A state-of-the-art multilingual embedding model from BAAI.
- **Pydantic:** A Python library for data validation using type hints, forcing the LLM to output predictable JSON.
- **Human-in-the-loop (HITL):** Designing the system to pause or escalate to a human before taking critical or irreversible actions.
