import os
from pathlib import Path
from typing import List, Dict

class DocumentLoader:
    def __init__(self, directory: str):
        self.directory = Path(directory)

    def load(self) -> List[Dict[str, str]]:
        documents = []
        if not self.directory.exists():
            return documents
            
        for file_path in self.directory.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "name": file_path.name,
                    "content": content
                })
        return documents
