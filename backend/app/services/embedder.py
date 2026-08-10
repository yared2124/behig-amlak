from sentence_transformers import SentenceTransformer
from app.core.config import settings

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model_name)
    
    def encode(self, text: str):
        return self.model.encode(text).tolist()

embedder = Embedder()