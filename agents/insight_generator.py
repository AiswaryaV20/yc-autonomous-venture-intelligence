from db.database import SessionLocal
from db.models import Company
import random

PROMPT_VERSION = "v1.0-local-analysis"


def generate_insight(company):
    name = company.name

    # Simple AI-like reasoning logic
    growth_score = random.randint(50, 90)
    risk_score = random.randint(20, 70)
    innovation_score = random.randint(60, 95)

    summary = f"{name} is a YC-backed company operating in its respective domain."

    growth_text = f"Growth potential appears moderate to strong based on YC backing."
    risk_text = f"Risk level appears manageable but depends on market competition."
    innovation_text = f"The company demonstrates innovation typical of YC startups."

    return {
        "summary": summary,
        "growth_score": growth_score,
        "risk_score": risk_score,
        "innovation_score": innovation_score,
        "growth_text": growth_text,
        "risk_text": risk_text,
        "innovation_text": innovation_text
    }


def run_insight_generation():
    session = SessionLocal()
    companies = session.query(Company).all()

    for company in companies:
        insight = generate_insight(company)

        print("Generated insight for:", company.name)

    session.close()


if __name__ == "__main__":
    run_insight_generation()