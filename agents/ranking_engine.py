from db.database import SessionLocal
from sqlalchemy import text


def rank_companies():

    session = SessionLocal()

    rows = session.execute(
        text("""
            SELECT c.id, c.name, ai.insight_text
            FROM companies c
            JOIN ai_insights ai ON c.id = ai.company_id
            WHERE ai.insight_type = 'SUMMARY'
        """)
    ).fetchall()

    company_scores = []

    for row in rows:
        company_id = row[0]
        name = row[1]
        text_data = row[2]

        # Extract Growth Score from text
        try:
            growth_line = [line for line in text_data.split("\n") if "Growth Score" in line][0]
            growth_score = int(growth_line.split(":")[1].strip())
        except:
            growth_score = 0

        company_scores.append((company_id, name, growth_score))

    # Sort descending by growth score
    ranked = sorted(company_scores, key=lambda x: x[2], reverse=True)

    print("Top 10 High Growth Companies:")

    for company in ranked[:10]:
        print(company[1], "→ Growth Score:", company[2])

    session.close()


if __name__ == "__main__":
    rank_companies()