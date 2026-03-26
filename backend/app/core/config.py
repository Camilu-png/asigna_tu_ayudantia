import os

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def _build_database_url() -> str:
    user = POSTGRES_USER or ""
    password = f":{POSTGRES_PASSWORD}" if POSTGRES_PASSWORD else ""
    host_port = f"{POSTGRES_HOST}:{POSTGRES_PORT}" if POSTGRES_PORT else POSTGRES_HOST
    db = POSTGRES_DB or "asigna_tu_ayudantia"
    return f"postgresql+asyncpg://{user}{password}@{host_port}/{db}"


DATABASE_URL = _build_database_url()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
