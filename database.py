from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:Aishu%40123@localhost:5432/yc_intelligence"

# Create engine
engine = create_engine(DATABASE_URL)

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()