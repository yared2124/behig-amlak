import chromadb
from app.services.embedder import embedder
from app.core.config import settings

class RAGPipeline:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.collection = self.client.get_or_create_collection("ethiopian_laws")
    
    def search(self, query: str, top_k: int = 5):
        query_vector = embedder.encode(query)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas"]
        )
        return results["documents"][0]  # Returns list of text chunks

rag = RAGPipeline()