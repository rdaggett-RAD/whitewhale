from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whitewhale"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Apollo
    APOLLO_API_KEY: str = ""

    # NewsAPI
    NEWSAPI_KEY: str = ""

    # SerpAPI
    SERPAPI_KEY: str = ""

    # Unipile (LinkedIn)
    UNIPILE_API_KEY: str = ""
    UNIPILE_DSN: str = ""
    UNIPILE_WEBHOOK_SECRET: str = ""

    # Resend (Email)
    RESEND_API_KEY: str = ""

    # Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # App
    APP_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
