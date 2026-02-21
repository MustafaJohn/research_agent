import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class VectorMemory:
    """
    Persistent vector memory store using FAISS.
    Stores: {id, url, chunk, embedding}
    Capabilities:
      - add new chunks only if they aren't duplicates
      - retrieve relevant chunks based on similarity
      - persistent index + metadata across runs
    """

    def __init__(self, 
                 index_path=None,
                 meta_path=None,
                 model_name=None):
        from config import Config
        
        self.index_path = str(index_path or Config.MEMORY_INDEX_PATH)
        self.meta_path = str(meta_path or Config.MEMORY_META_PATH)
        model_name = model_name or Config.EMBEDDING_MODEL
        
        self.model = SentenceTransformer(model_name)
        
        # memory metadata structure
        self.memory = []  # list of dicts {id, url, chunk}
        self.next_id = 0
        
        # vector index
        self.dimension = 384  # all-MiniLM-L6-v2 embeddings size
        self.index = faiss.IndexFlatIP(self.dimension)
        print("VectorMemory instance:", id(self))
        self._load()

    def _load(self):
        """Load metadata + index if exists."""
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.memory = json.load(f)
                if self.memory:
                    self.next_id = max(m["id"] for m in self.memory) + 1

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

    def _save(self):
        """Persist metadata + index."""
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)
        faiss.write_index(self.index, self.index_path)

    def _embed(self, text):
        return self.model.encode([text], convert_to_numpy=True)

    def _chunk_text(self, text, max_words=200):
        """Split long text into chunks to avoid huge embeddings."""
        words = text.split()
        for i in range(0, len(words), max_words):
            yield " ".join(words[i:i + max_words])

    """def add_document(self, url, text):
        
            Split text, embed chunks, store in memory.
            Returns list of tuples: (chunk_id, chunk_text)
        
        stored_chunks = []

        for chunk in self._chunk_text(text):
            if self._is_duplicate(chunk):
                continue

            emb = self._embed(chunk)
            self.index.add(emb)

            self.memory.append({
                "id": self.next_id,
                "url": url,
                "chunk": chunk,
            })

            #stored_chunks = self.memory  # store chunk_id + text
            self.next_id += 1
            stored_chunks.append((self.next_id - 1, chunk))
        self._save()
        return stored_chunks  """
    
    def add_chunks(self, url, chunks):
        """
        chunks: List[(chunk_id, chunk_text)]
        """
        stored_chunks = []

        for chunk_id, chunk_text in chunks:
            
            emb = self._embed(chunk_text)
            if self._is_duplicate(emb):
                continue
            faiss.normalize_L2(emb)
            self.index.add(emb)

            self.memory.append({
                "id": self.next_id,
                "url": url,
                "chunk": chunk_text,
            })

            stored_chunks.append((self.next_id, chunk_text))
            self.next_id += 1

        self._save()
        return stored_chunks


    def _is_duplicate(self, chunk_emb, threshold=0.90):
        """Detect duplicates via cosine similarity."""
        if len(self.memory) < 1:
            return False
            
        scores, _ = self.index.search(chunk_emb, 1)  # nearest neighbor
        
        if scores[0][0] > threshold:  
            return True
        return False

    def search(self, query, k=5):
        results = []
        emb = self._embed(query)
        faiss.normalize_L2(emb)
        scores, ids = self.index.search(emb, k)
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0 or idx >= len(self.memory):
                continue
            m = self.memory[idx]
            results.append({
                "score": float(score),
                "url": m["url"],
                "chunk": m["chunk"]
            })
        print("FAISS index size:", self.index.ntotal)
        print("Memory size:", len(self.memory))
        return results