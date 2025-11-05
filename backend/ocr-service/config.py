from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Invoice OCR Service"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Self-hosted OCR service using PaddleOCR for invoice processing"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS Settings - will be split from comma-separated string
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    # OCR Settings
    OCR_USE_GPU: bool = False
    OCR_LANGUAGE: str = "en"
    OCR_USE_ANGLE_CLS: bool = False  # Disabled for speed - most invoices are straight
    OCR_DET_DB_THRESH: float = 0.3
    OCR_DET_DB_BOX_THRESH: float = 0.5
    
    # File Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
    TEMP_DIR: str = "temp"
    
    # Processing Settings
    PDF_DPI: int = 150  # Further reduced from 200 for faster processing (3x speed boost)
    IMAGE_MAX_SIZE: int = 2048  # Further reduced from 3072 for faster OCR
    CONFIDENCE_THRESHOLD: float = 0.4  # Slightly lowered to catch more text
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
