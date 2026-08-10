import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Free LLM via Groq
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # Free Embedding model from Hugging Face
    embedding_model_name: str = "rasyosef/embedding-amharic-medium"
    
    # Databases
    chroma_db_path: str = "./app/data/chroma_db"
    postgres_database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/behig_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        env_file = ".env"

settings = Settings()