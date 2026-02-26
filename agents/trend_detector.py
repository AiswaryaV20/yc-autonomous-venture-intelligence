from db.database import SessionLocal
from sqlalchemy import text
from datetime import datetime

PROMPT_VERSION = "v2.0-trend-analysis"
MODEL_NAME = "cross-company-trend-engine"


def detect_trends():
    session = SessionLocal()

    print("\n--- Running Advanced Trend Detector ---")

    # 1️⃣ Count companies by domain
    rows = session.execute(
        text("""
            SELECT domain, COUNT(*) as count
            FROM companies
            WHERE domain IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
        """)
    ).fetchall()

    if not rows:
        print("No company data found.")
        session.close()
        return

    # Top 5 dominant sectors
    top_domains = rows[:5]

    for domain, count in top_domains:

        explanation = f"""
Trend Detected: {domain}

This sector has {count} companies in the YC dataset,
making it one of the dominant startup categories.

Signal Strength:
- High company concentration
- Indicates ecosystem focus
- Possible investor interest cluster
"""

        # Store trend insight
        session.execute(
            text("""
                INSERT INTO ai_insights
                (company_id, insight_type, insight_text, confidence_score, model_name, prompt_version, created_at)
                VALUES (NULL, :type, :text, :confidence, :model, :version, :created)
            """),
            {
                "type": "TREND",
                "text": explanation,
                "confidence": 0.85,
                "model": MODEL_NAME,
                "version": PROMPT_VERSION,
                "created": datetime.now()
            }
        )

        print(f"Stored trend for domain: {domain}")

    session.commit()
    session.close()

    print("--- Advanced Trend Detection Complete ---\n")


if __name__ == "__main__":
    detect_trends()