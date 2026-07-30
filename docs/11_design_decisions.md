# Design Decisions (ADRs)

## 1. Groq for LLM Inference
- **Decision:** Use Groq API with `llama-3.3-70b-versatile`.
- **Alternatives:** OpenAI GPT-4o, local Llama3 via Ollama.
- **Why chosen:** Groq provides near-instantaneous inference (LPU), which is critical for latency in a multi-agent chained workflow where 4-5 LLM calls happen sequentially.

## 2. Multi-Agent Orchestration (LangGraph)
- **Decision:** Split pipeline into Intake, Triage, Extraction, Resolution, Response nodes.
- **Alternatives:** Single massive prompt, LangChain LCEL.
- **Why chosen:** Better observability, easier debugging, allows conditional skipping (e.g., safety guardrail skips extraction), and enforces schema constraints per task.

## 3. Local Embeddings & FAISS
- **Decision:** Use `BAAI/bge-m3` via `sentence-transformers` and `faiss-cpu`.
- **Alternatives:** OpenAI Embeddings + Pinecone.
- **Why chosen:** Avoids API costs, ensures data privacy (critical for government/metro operations), and BGE-M3 handles multilingual queries excellently.

## 4. SQLite for Operational State
- **Decision:** Use SQLite via SQLAlchemy.
- **Alternatives:** Storing state in FAISS, or in-memory dicts.
- **Why chosen:** Vector databases cannot do relational math (like counting officer active cases vs capacity). SQLite provides ACID transactions for these operational requirements.
