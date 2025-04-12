from prettyconf import config

# Determine the environment type: "dev" or "prod"
ENV_TYPE = config("ENV_TYPE", default="dev")

# Set the debug flag based on environment
DEBUG = config(
    "DEBUG",
    default=(ENV_TYPE.lower() == "dev"),
    cast=bool,
)

# Database URL configuration for different environments
if ENV_TYPE.lower() == "prod":
    DATABASE_URL = config(
        "DATABASE_URL",
        default="postgresql://prod_user:prod_pass@db-server:5432/huuva_prod_db",
    )
else:
    DATABASE_URL = config(
        "DATABASE_URL",
        default="postgresql://dev_user:dev_pass@localhost:5432/huuva_dev_db",
    )

# Sentry DSN for error tracking and logging (empty string if not set)
SENTRY_DSN = config("SENTRY_DSN", default="", required=False)

# Optional: Set logging level (e.g., INFO, DEBUG)
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
