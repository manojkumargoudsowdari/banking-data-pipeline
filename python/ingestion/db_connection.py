import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

REQUIRED_ENV_VARS = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]


def validate_environment():
    load_dotenv()
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        missing = ", ".join(missing_vars)
        raise RuntimeError(f"Missing required environment variable(s): {missing}")


def get_postgres_engine():
    validate_environment()

    try:
        port = int(os.environ["POSTGRES_PORT"])
    except ValueError as exc:
        raise RuntimeError("POSTGRES_PORT must be a valid integer.") from exc

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=port,
        database=os.environ["POSTGRES_DB"],
    )

    return create_engine(url, pool_pre_ping=True)
