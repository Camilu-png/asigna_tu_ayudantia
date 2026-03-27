import os

POSTGRES_DB = os.getenv("POSTGRES_DB", "asigna_tu_ayudantia")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def _build_database_url() -> str:
    user = POSTGRES_USER or ""
    password = f":{POSTGRES_PASSWORD}" if POSTGRES_PASSWORD else ""
    host_port = f"{POSTGRES_HOST}:{POSTGRES_PORT}" if POSTGRES_PORT else POSTGRES_HOST
    return f"postgresql+asyncpg://{user}{password}@{host_port}/{POSTGRES_DB}"


DATABASE_URL = _build_database_url()

_allow_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [
    origin.strip() for origin in _allow_origins.split(",") if origin.strip()
]

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
