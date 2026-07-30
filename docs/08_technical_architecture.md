# Technical Architecture

## Local Prototype Architecture
```mermaid
graph TD
    PB[Passenger Browser] --> AUTH[Authentication & RBAC]
    SB[Staff Browser] --> AUTH
    
    AUTH --> UI_PASS[Streamlit Passenger Portal]
    AUTH --> UI_STAFF[Streamlit Staff Portal]
    
    UI_PASS --> ORCH[LangGraph Orchestration]
    UI_STAFF --> DB[(SQLite DB)]
    
    ORCH --> AGENTS[Agentic Processing]
    AGENTS --> GROQ[Groq API]
    
    AGENTS --> TOOLS[Tools]
    TOOLS --> DB
    
    AGENTS --> RAG[RAG Retriever]
    RAG --> BGE[bge-m3 Embeddings]
    BGE --> FAISS[(FAISS Vector DB)]
```

## Production AWS Architecture

If we were to scale this for the actual Chennai Metro, the architecture would enforce strict security and access boundaries:

- **Passenger Portal:** A React Native mobile app or web frontend communicating via an API Gateway.
- **Staff Portal:** A distinct React internal web dashboard behind a VPN/Zero-Trust proxy.
- **Authentication:** AWS Cognito or Auth0, passing JWTs containing the user's role (`PASSENGER` vs `OFFICER`). These JWTs would be validated at the API Gateway, ensuring AI agents never directly handle passwords or auth tokens.
- **Orchestration:** LangGraph Cloud or AWS Step Functions orchestrating the AI pipeline asynchronously on ECS (Fargate).
- **Database:** Amazon RDS PostgreSQL, storing operational state and enforcing row-level security (so passengers can only query `WHERE user_id = :my_id`).
- **Knowledge Base:** Amazon OpenSearch Serverless replacing local FAISS for scaled vector searches over thousands of SOPs.
