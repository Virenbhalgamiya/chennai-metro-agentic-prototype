import uuid
from typing import List
from src.models.schemas import KnowledgeChunk

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, documents: List[dict]) -> List[KnowledgeChunk]:
        chunks = []
        for doc in documents:
            text = doc["content"]
            name = doc["name"]
            
            # Very simple chunking for demo purposes
            words = text.split()
            for i in range(0, len(words), self.chunk_size - self.overlap):
                chunk_words = words[i:i + self.chunk_size]
                if not chunk_words:
                    break
                
                chunk_text = " ".join(chunk_words)
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_name=name,
                        content=chunk_text,
                        metadata={"source": name, "start_word": i}
                    )
                )
        return chunks
