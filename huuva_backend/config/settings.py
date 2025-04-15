from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = True
    PRODUCTION: bool = False
    ENVIRONMENT: str = "development"

    # This should be empty as it will be set in the .env file, but for example purposes,
    # we set it here.
    DATABASE_URL: str = "postgresql://dev_user:dev_pass@localhost:5432/huuva_dev_db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
