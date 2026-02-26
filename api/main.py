from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from db.database import SessionLocal
from embeddings.semantic_search import search
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# -----------------------------------
# Initialize FastAPI
# -----------------------------------

app = FastAPI()

# -----------------------------------
# CORS (Allow frontend connection)
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all temporarily (fixes fetch error)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# Request Model
# -----------------------------------

class QuestionRequest(BaseModel):
    question: str


# -----------------------------------
# AI Ask Endpoint
# -----------------------------------

@app.post("/api/ask")
def ask_question(request: QuestionRequest):

    session = SessionLocal()

    try:
        results = search(request.question, top_k=5)

        if not results:
            return {
                "question": request.question,
                "answer": "No relevant companies found.",
                "cited_companies": [],
                "reasoning_trace": []
            }

        company_names = []
        reasoning_trace = []

        for company in results:

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

            if insight:
                company_names.append(company.name)

                reasoning_trace.append(
                    f"{company.name} selected due to embedding similarity."
                )

        explanation = f"""
Query: {request.question}

Relevant Companies:
{', '.join(company_names)}

Selection Logic:
- Semantic embedding similarity
- Deterministic AI scoring
- Stored analytical insights
        """.strip()

        return {
            "question": request.question,
            "answer": explanation,
            "cited_companies": company_names,
            "reasoning_trace": reasoning_trace
        }

    except Exception as e:
        return {
            "error": str(e)
        }

    finally:
        session.close()


# -----------------------------------
# Dashboard Endpoint
# -----------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    session = SessionLocal()

    stats = session.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM companies),
            (SELECT COUNT(*) FROM ai_insights),
            (SELECT COUNT(*) FROM ai_tasks WHERE status='COMPLETED'),
            (SELECT COUNT(*) FROM ai_tasks WHERE status='FAILED'),
            (SELECT COUNT(*) FROM ai_tasks WHERE status='PENDING')
    """)).fetchone()

    performance = session.execute(text("""
        SELECT
            COALESCE(AVG(execution_time),0),
            COALESCE(AVG(token_usage),0)
        FROM ai_tasks
        WHERE status='COMPLETED'
    """)).fetchone()

    session.close()

    html_content = f"""
    <html>
    <head>
        <title>AI Intelligence Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body style="font-family: Arial; margin:40px;">

        <h1>🚀 AI Intelligence Dashboard</h1>

        <h2>System Overview</h2>
        <ul>
            <li>Total Companies: {stats[0]}</li>
            <li>Total Insights: {stats[1]}</li>
            <li>Completed Tasks: {stats[2]}</li>
            <li>Failed Tasks: {stats[3]}</li>
            <li>Pending Tasks: {stats[4]}</li>
        </ul>

        <h2>Performance Metrics</h2>
        <ul>
            <li>Average Execution Time: {round(performance[0],4)} sec</li>
            <li>Average Token Usage: {int(performance[1])} tokens</li>
        </ul>

        <canvas id="taskChart"></canvas>

        <script>
            const ctx = document.getElementById('taskChart');

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Completed', 'Failed', 'Pending'],
                    datasets: [{{
                        label: 'Task Count',
                        data: [{stats[2]}, {stats[3]}, {stats[4]}],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>

    </body>
    </html>
    """

    return html_content
@app.get("/api/venture-rankings")
def get_venture_rankings():

    session = SessionLocal()

    rows = session.execute(
        text("""
            SELECT c.name,
                   v.opportunity_score,
                   v.recommendation,
                   v.created_at
            FROM venture_scores v
            JOIN companies c ON c.id = v.company_id
            ORDER BY v.opportunity_score DESC
            LIMIT 10
        """)
    ).fetchall()

    session.close()

    rankings = []

    for row in rows:
        rankings.append({
            "company": row[0],
            "opportunity_score": row[1],
            "recommendation": row[2],
            "evaluated_at": str(row[3])
        })

    return {
        "top_venture_opportunities": rankings
    }