from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    yc_company_id = Column(String, unique=True)
    name = Column(String)
    domain = Column(String)
    first_seen_at = Column(TIMESTAMP, server_default=func.now())
    last_seen_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)


class CompanySnapshot(Base):
    __tablename__ = "company_snapshots"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    raw_data = Column(JSONB)
    snapshot_hash = Column(String)
    scraped_at = Column(TIMESTAMP, server_default=func.now())


class CompanyEmbedding(Base):
    __tablename__ = "company_embeddings"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    embedding = Column(Text)   # replaced VECTOR with TEXT
    source_type = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    insight_type = Column(String)
    insight_text = Column(Text)
    confidence_score = Column(Float)
    model_name = Column(String)
    prompt_version = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class AITask(Base):
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    status = Column(String)
    input_payload = Column(JSONB)
    output_payload = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)