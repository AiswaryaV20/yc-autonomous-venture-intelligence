from sqlalchemy import Column, Integer, Boolean, JSON, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    yc_company_id = Column(Text, unique=True, index=True)
    name = Column(Text)
    domain = Column(Text)
    first_seen_at = Column(TIMESTAMP, default=func.now())
    last_seen_at = Column(TIMESTAMP, default=func.now())
    is_active = Column(Boolean)


class CompanySnapshot(Base):
    __tablename__ = "company_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    raw_data = Column(JSON)
    snapshot_hash = Column(Text)
    scraped_at = Column(TIMESTAMP, default=func.now())