import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Required environment variables
    groq_api_key: str
    database_url: str   # <-- ADD THIS

    # Optional with defaults
    embedding_model_name: str = "rasyosef/embedding-amharic-medium"
    chroma_db_path: str = "./app/data/chroma_db"
    redis_url: str = "redis://localhost:6379"

    # Configure Pydantic to read from .env and ignore extra fields
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # <-- KEY: prevents validation errors for unknown env vars
    )

# Create a single instance to import elsewhere
settings = Settings()