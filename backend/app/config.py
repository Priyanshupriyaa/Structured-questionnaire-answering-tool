import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SecureSync Questionnaire Tool"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./questionnaire_tool.db"
    
    # JWT - REQUIRED: Must be set in environment variables
    SECRET_KEY: str = ""  # Required - set in .env file
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # RAG settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.5
    
    # Upload settings
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()

# Validate required settings
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env file")

# Create upload directory if not exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
