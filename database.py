from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ Replace yourpassword with your PostgreSQL password
DATABASE_URL = "postgresql://postgres:Aishu@123@localhost:5432/yc_ai"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()