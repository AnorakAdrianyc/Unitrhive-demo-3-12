"""Configuration settings for UniThrive."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "UniThrive Prototype"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Data
    data_dir: str = "data"
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Risk Detection
    high_risk_keywords: List[str] = [
        "suicidal", "self-harm", "kill myself", "end it all",
        "no point living", "want to die", "better off dead"
    ]
    medium_risk_keywords: List[str] = [
        "cannot cope", "hopeless", "worthless", "extreme stress",
        "can't sleep for days", "overwhelmed", "isolated",
        "no one cares", "giving up"
    ]
    
    # Scoring Weights
    mental_ring_weights: dict = {
        "course_engagement": 0.40,
        "skill_development": 0.30,
        "workshops": 0.15,
        "projects": 0.15
    }
    
    psych_ring_weights: dict = {
        "emotional_stability": 0.30,
        "self_awareness": 0.30,
        "cognitive_health": 0.20,
        "risk_mitigation": 0.20
    }
    
    physical_ring_weights: dict = {
        "time_management": 0.25,
        "activity": 0.25,
        "sleep": 0.25,
        "fitness": 0.25
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
