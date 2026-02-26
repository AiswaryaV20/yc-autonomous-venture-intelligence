from db.database import SessionLocal
from sqlalchemy import text
from datetime import datetime


def generate_report():

    session = SessionLocal()

    # Top 5 venture opportunities
    top_companies = session.execute(text("""
        SELECT c.name, v.opportunity_score, v.recommendation
        FROM venture_scores v
        JOIN companies c ON c.id = v.company_id
        ORDER BY v.opportunity_score DESC
        LIMIT 5
    """)).fetchall()

    # Emerging sectors (simple domain clustering)
    sector_data = session.execute(text("""
        SELECT domain, COUNT(*)
        FROM companies
        WHERE domain IS NOT NULL
        GROUP BY domain
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """)).fetchall()

    session.close()

    # Build Natural Language Report
    report = f"""
🚀 YC Autonomous Venture Intelligence Report
Generated: {datetime.now()}

Top Venture Opportunities:
"""

    for company in top_companies:
        report += f"""
- {company[0]}
  Opportunity Score: {company[1]}
  Recommendation: {company[2]}
"""

    report += "\nEmerging Sectors:\n"

    for sector in sector_data:
        report += f"- {sector[0]} ({sector[1]} companies)\n"

    report += """

Strategic Insight:
The current YC landscape indicates strong clustering in emerging
technology-driven sectors. Companies scoring highest demonstrate
balanced growth and innovation metrics with controlled risk exposure.

Recommendation:
Focus investment research on high-opportunity AI and tech-enabled
infrastructure startups showing deterministic growth signals.
"""

    # Store report
    session = SessionLocal()
    session.execute(
        text("""
            INSERT INTO venture_reports (report_text, generated_at)
            VALUES (:report, :created)
        """),
        {
            "report": report,
            "created": datetime.now()
        }
    )
    session.commit()
    session.close()

    print("✅ Autonomous Venture Report Generated")


if __name__ == "__main__":
    generate_report()