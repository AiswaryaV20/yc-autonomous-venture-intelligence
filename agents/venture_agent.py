from db.database import SessionLocal
from db.models import Company
from sqlalchemy import text
from datetime import datetime

def calculate_opportunity(growth, innovation, risk):
    score = (growth * 0.4) + (innovation * 0.4) - (risk * 0.2)
    return max(0, min(100, int(score)))


def generate_recommendation(score):
    if score > 80:
        return "STRONG BUY – High venture potential"
    elif score > 65:
        return "BUY – Promising growth signals"
    elif score > 50:
        return "HOLD – Moderate opportunity"
    else:
        return "AVOID – Weak risk-reward profile"


def run_venture_agent():

    session = SessionLocal()

    companies = session.query(Company).all()

    for company in companies:

        # Pull latest summary insight
        insight = session.execute(
            text("""
                SELECT insight_text
                FROM ai_insights
                WHERE company_id = :cid
                AND insight_type = 'SUMMARY'
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"cid": company.id}
        ).fetchone()

        if not insight:
            continue

        # Extract simple deterministic scores from insight
        text_data = insight[0]

        try:
            growth = int(text_data.split("Growth Score:")[1].split("\n")[0].strip())
            innovation = int(text_data.split("Innovation Score:")[1].split("\n")[0].strip())
            risk = int(text_data.split("Risk Score:")[1].split("\n")[0].strip())
        except:
            continue

        opportunity_score = calculate_opportunity(growth, innovation, risk)
        recommendation = generate_recommendation(opportunity_score)

        session.execute(
            text("""
                INSERT INTO venture_scores
                (company_id, growth_score, innovation_score, risk_score,
                 opportunity_score, recommendation, created_at)
                VALUES (:cid, :g, :i, :r, :o, :rec, :created)
            """),
            {
                "cid": company.id,
                "g": growth,
                "i": innovation,
                "r": risk,
                "o": opportunity_score,
                "rec": recommendation,
                "created": datetime.now()
            }
        )

        print(f"Scored: {company.name} → {opportunity_score}")

    session.commit()
    session.close()


if __name__ == "__main__":
    run_venture_agent()