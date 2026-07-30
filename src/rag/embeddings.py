import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model {model_name}...")
        self.model = SentenceTransformer(model_name)
        
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

    def embed_query(self, query: str) -> np.ndarray:
        # BGE-M3 handles queries well.
        return self.model.encode([query], normalize_embeddings=True)[0]
