from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔴 Replace YOURPASSWORD with your actual PostgreSQL password
DATABASE_URL = "postgresql://postgres:Aishu%40123@localhost:5432/yc_ai"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()