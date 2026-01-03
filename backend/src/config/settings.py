"""
Configuration settings for Land Optimization Backend
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application Info
    APP_NAME: str = "AI Land Optimization Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # CORS Settings (Allow file:// via null origin + localhost URLs)
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "null"  # For file:// protocol (HTML dashboard)
    ]
    CORS_ALLOW_CREDENTIALS: bool = False  # Set to False to allow file:// origins
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/land_optimization"
    DATABASE_ECHO: bool = False  # Set to True to see SQL queries in logs

    # Redis Cache Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 3600  # Cache time-to-live in seconds (1 hour)

    # Genetic Algorithm Parameters
    # INCREASED for better convergence and non-overlapping solutions
    GA_GENERATIONS: int = 200  # Increased from 100 - more time to find non-overlapping layouts
    GA_POPULATION_SIZE: int = 100  # Increased from 50 - more diversity
    GA_MUTATION_RATE: float = 0.15  # Increased from 0.1 - more exploration
    GA_CROSSOVER_RATE: float = 0.85  # Increased from 0.8 - more combination
    GA_TOURNAMENT_SIZE: int = 5  # Increased from 3 - stronger selection pressure

    # File Storage
    OUTPUT_DIR: str = "./output"
    TEMP_DIR: str = "./temp"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "./logs/app.log"
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True

    # Sri Lankan Building Rules Toggle
    ENABLE_SRI_LANKAN_RULES: bool = True
    SETBACK_FRONT: float = 3.0  # meters
    SETBACK_SIDE: float = 1.5   # meters
    SETBACK_BACK: float = 1.5   # meters
    MAX_COVERAGE_PERCENT: float = 65.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
