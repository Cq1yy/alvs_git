import os


def get_database_url() -> str:
    # Значение по умолчанию удобно для docker compose
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/app",
    )


def get_log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO")
