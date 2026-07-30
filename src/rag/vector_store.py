import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
from src.models.schemas import KnowledgeChunk

class VectorStore:
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.index_file = self.index_path / "faiss.index"
        self.metadata_file = self.index_path / "metadata.pkl"
        self.index = None
        self.chunks: List[KnowledgeChunk] = []
        self.dimension = 384 # MiniLM dim

    def build_index(self, chunks: List[KnowledgeChunk], embeddings: np.ndarray):
        self.chunks = chunks
        self.index = faiss.IndexFlatIP(self.dimension) # Inner product for normalized embeddings (Cosine Similarity)
        
        if len(embeddings) > 0:
            self.index.add(np.array(embeddings, dtype=np.float32))
            
        self._save()

    def _save(self):
        self.index_path.mkdir(exist_ok=True, parents=True)
        if self.index:
            faiss.write_index(self.index, str(self.index_file))
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.chunks, f)

    def load_index(self) -> bool:
        if self.index_file.exists() and self.metadata_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "rb") as f:
                self.chunks = pickle.load(f)
            return True
        return False

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[KnowledgeChunk, float]]:
        if not self.index or len(self.chunks) == 0:
            return []
            
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(dist)))
        return results
