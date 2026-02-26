from db.database import SessionLocal
from sqlalchemy import text
from datetime import datetime
from agents.task_creator import create_analysis_tasks

scheduler.add_job(create_analysis_tasks, 'interval', minutes=10)

def create_analysis_tasks():

    session = SessionLocal()

    companies = session.execute(
        text("SELECT id FROM companies")
    ).fetchall()

    created_count = 0

    for company in companies:

        exists = session.execute(
            text("""
                SELECT 1 FROM ai_tasks
                WHERE task_type='ANALYZE_COMPANY'
                AND input_payload->>'company_id' = :cid
                AND status IN ('PENDING','RUNNING')
            """),
            {"cid": str(company[0])}
        ).fetchone()

        if not exists:
            session.execute(
                text("""
                    INSERT INTO ai_tasks
                    (task_type, status, input_payload, created_at)
                    VALUES (:type, 'PENDING', :payload, :created)
                """),
                {
                    "type": "ANALYZE_COMPANY",
                    "payload": f'{{"company_id": {company[0]}}}',
                    "created": datetime.now()
                }
            )
            created_count += 1

    session.commit()
    session.close()

    print(f"Created {created_count} new analysis tasks.")