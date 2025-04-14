from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True

    # This should be empty as it will be set in the .env file, but for example purposes, we set it here.
    DATABASE_URL: str = "postgresql://dev_user:dev_pass@localhost:5432/huuva_dev_db"

    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
