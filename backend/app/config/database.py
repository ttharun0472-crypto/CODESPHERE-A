import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


# Load .env file
BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=BACKEND_ENV_FILE, override=False)


# Database information
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Validate database settings
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError(
        "Database configuration missing. Check DB_HOST, DB_USER, "
        "DB_PASSWORD, and DB_NAME in your .env file."
    )


# PostgreSQL connection with SSL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
    query={"sslmode": "require"},
)


# Database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)


# Ensure required email OTP columns exist
def ensure_email_otp_columns():
    required_columns = {
        "email_otp_challenges": {
            "purpose": "VARCHAR(32) NOT NULL DEFAULT 'login'",
            "verified": "BOOLEAN NOT NULL DEFAULT FALSE",
            "verified_at": "TIMESTAMP",
        }
    }

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            for column_name, column_sql in columns.items():
                query = text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema = 'public' "
                    "AND table_name = :table_name "
                    "AND column_name = :column_name"
                )

                existing = connection.execute(
                    query,
                    {
                        "table_name": table_name,
                        "column_name": column_name,
                    },
                ).first()

                if existing is None:
                    connection.execute(
                        text(
                            f'ALTER TABLE public."{table_name}" '
                            f'ADD COLUMN IF NOT EXISTS "{column_name}" '
                            f'{column_sql}'
                        )
                    )


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base for models
Base = declarative_base()


# Get database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()