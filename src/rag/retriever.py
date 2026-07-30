import logging
from typing import List, Dict, Any
from src.rag.loader import DocumentLoader
from src.rag.chunker import DocumentChunker
from src.rag.embeddings import EmbeddingService
from src.rag.vector_store import VectorStore
from src.config.settings import SOP_DIR, FAISS_INDEX_PATH, RAG_TOP_K

logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self):
        self.loader = DocumentLoader(str(SOP_DIR))
        self.chunker = DocumentChunker()
        self.store = VectorStore(str(FAISS_INDEX_PATH))
        self.embeddings = None
        
    def initialize(self):
        if self.store.load_index():
            logger.info("Loaded existing FAISS index.")
            return

        logger.info("Building FAISS index from mock SOPs...")
        if not self.embeddings:
            self.embeddings = EmbeddingService()
            
        docs = self.loader.load()
        chunks = self.chunker.chunk(docs)
        
        if chunks:
            texts = [c.content for c in chunks]
            embeds = self.embeddings.embed_texts(texts)
            self.store.build_index(chunks, embeds)
            logger.info(f"Indexed {len(chunks)} chunks.")
        else:
            logger.warning("No documents found to index.")

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or RAG_TOP_K
        if not self.store.index:
            self.initialize()
            
        if not self.embeddings:
            self.embeddings = EmbeddingService()
            
        query_embed = self.embeddings.embed_query(query)
        results = self.store.search(query_embed, k)
        
        return [
            {
                "chunk_id": chunk.chunk_id,
                "document_name": chunk.document_name,
                "content": chunk.content,
                "score": score
            }
            for chunk, score in results
        ]
