from db.database import SessionLocal
from db.models import Company
from sqlalchemy import text
from datetime import datetime
from agents.change_detector import detect_snapshot_changes
import time

PROMPT_VERSION = "v2.0-deterministic"
MODEL_NAME = "deterministic-analysis-engine"


# ----------------------------
# SCORING ENGINE
# ----------------------------

def calculate_scores(company):

    growth_score = 50
    innovation_score = 50
    risk_score = 30

    growth_reason = []
    innovation_reason = []
    risk_reason = []

    if company.domain:
        domain_upper = company.domain.upper()

        if "AI" in domain_upper:
            growth_score += 15
            innovation_score += 20
            growth_reason.append("Operating in AI sector (high growth market)")
            innovation_reason.append("AI-driven business model")

        if "FINTECH" in domain_upper:
            growth_score += 10
            innovation_score += 10
            growth_reason.append("Fintech market expansion")
            innovation_reason.append("Financial technology innovation")

    if company.is_active:
        growth_score += 10
        growth_reason.append("Company currently active")
    else:
        risk_score += 40
        risk_reason.append("Company marked inactive")

    if not company.domain:
        risk_score += 10
        risk_reason.append("Missing domain data")

    return (
        min(100, growth_score),
        min(100, innovation_score),
        min(100, risk_score),
        growth_reason,
        innovation_reason,
        risk_reason,
    )


# ----------------------------
# INSIGHT GENERATOR
# ----------------------------

def generate_insight(company):

    (
        growth_score,
        innovation_score,
        risk_score,
        growth_reason,
        innovation_reason,
        risk_reason,
    ) = calculate_scores(company)

    summary = f"{company.name} is a YC-backed startup operating in {company.domain or 'an unspecified sector'}."

    insight_text = f"""
Summary:
{summary}

Growth Score: {growth_score}
Reason:
- {'; '.join(growth_reason) if growth_reason else 'Baseline growth assessment'}

Innovation Score: {innovation_score}
Reason:
- {'; '.join(innovation_reason) if innovation_reason else 'Standard innovation baseline'}

Risk Score: {risk_score}
Reason:
- {'; '.join(risk_reason) if risk_reason else 'No major risk signals detected'}
"""

    return insight_text


# ----------------------------
# TASK PROCESSOR
# ----------------------------

def process_tasks():

    session = SessionLocal()

    tasks = session.execute(
        text("""
            SELECT id, input_payload, retry_count
            FROM ai_tasks
            WHERE status = 'PENDING'
            ORDER BY created_at ASC
            LIMIT 20
        """)
    ).fetchall()

    for task in tasks:

        task_id = task[0]
        payload = task[1]
        retry_count = task[2]

        start_time = time.time()

        try:

            company_id = payload["company_id"]

            # Mark RUNNING
            session.execute(
                text("UPDATE ai_tasks SET status='RUNNING' WHERE id=:id"),
                {"id": task_id}
            )

            company = session.query(Company).filter_by(id=company_id).first()

            if not company:
                raise Exception("Company not found")

            # 🔥 Generate Insight
            insight_text = generate_insight(company)

            # 🔥 Change Detection
            change_text = detect_snapshot_changes(company.id)

            # Insert SUMMARY insight
            session.execute(
                text("""
                    INSERT INTO ai_insights
                    (company_id, insight_type, insight_text, confidence_score, model_name, prompt_version, created_at)
                    VALUES (:company_id, 'SUMMARY', :text, :confidence, :model, :version, :created)
                """),
                {
                    "company_id": company.id,
                    "text": insight_text,
                    "confidence": 0.85,
                    "model": MODEL_NAME,
                    "version": PROMPT_VERSION,
                    "created": datetime.now()
                }
            )

            # Insert ANOMALY insight if detected
            if change_text:
                session.execute(
                    text("""
                        INSERT INTO ai_insights
                        (company_id, insight_type, insight_text, confidence_score, model_name, prompt_version, created_at)
                        VALUES (:company_id, 'ANOMALY', :text, 0.9, 'change-detector', 'v1.0', :created)
                    """),
                    {
                        "company_id": company.id,
                        "text": change_text,
                        "created": datetime.now()
                    }
                )

            execution_time = time.time() - start_time
            token_usage = len(insight_text.split())

            # Mark COMPLETED
            session.execute(
                text("""
                    UPDATE ai_tasks
                    SET status='COMPLETED',
                        completed_at=:completed,
                        execution_time=:exec_time,
                        token_usage=:tokens
                    WHERE id=:id
                """),
                {
                    "id": task_id,
                    "completed": datetime.now(),
                    "exec_time": execution_time,
                    "tokens": token_usage
                }
            )

            print(f"Processed company: {company.name}")

        except Exception as e:

            # 🔥 Intelligent Retry Logic
            if retry_count < 3:
                session.execute(
                    text("""
                        UPDATE ai_tasks
                        SET status='PENDING',
                            retry_count = retry_count + 1,
                            error_message=:error
                        WHERE id=:id
                    """),
                    {"id": task_id, "error": str(e)}
                )
                print(f"Retrying task {task_id} (Attempt {retry_count + 1})")

            else:
                session.execute(
                    text("""
                        UPDATE ai_tasks
                        SET status='FAILED',
                            error_message=:error
                        WHERE id=:id
                    """),
                    {"id": task_id, "error": str(e)}
                )
                print(f"Task permanently failed: {task_id}")

        session.commit()

    session.close()


if __name__ == "__main__":
    process_tasks()