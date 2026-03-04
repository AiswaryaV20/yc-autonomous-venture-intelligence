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
    allow_origins=["*"],
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

        # 1️⃣ Semantic Search
        results = search(request.question, top_k=5)

        if not results:
            return {
                "question": request.question,
                "answer": "No relevant companies found.",
                "cited_companies": [],
                "reasoning_trace": [],
                "confidence": 0.2
            }

        cited_companies = []
        reasoning_trace = []

        for company in results:

            insight = session.execute(
                text("""
                    SELECT insight_text
                    FROM ai_insights
                    WHERE company_id = :cid
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"cid": company.id}
            ).fetchone()

            if insight:
                cited_companies.append(company.name)

                reasoning_trace.append(
                    f"{company.name} selected via semantic similarity and stored AI insights."
                )

        answer_text = f"""
Question: {request.question}

Relevant YC Companies:
{", ".join(cited_companies)}

These companies were retrieved using semantic vector similarity
and validated using stored AI insights in the database.
"""

        return {
            "question": request.question,
            "answer": answer_text.strip(),
            "cited_companies": cited_companies,
            "reasoning_trace": reasoning_trace,
            "confidence": 0.85
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        session.close()


# -----------------------------------
# Venture Rankings Endpoint
# -----------------------------------

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
            (SELECT COUNT(*) FROM venture_scores)
    """)).fetchone()

    session.close()

    html_content = f"""
    <html>
    <head>
        <title>YC AI Intelligence Dashboard</title>
    </head>
    <body style="font-family: Arial; margin:40px;">

        <h1>🚀 YC Autonomous Venture Intelligence</h1>

        <h2>System Overview</h2>

        <ul>
            <li>Total Companies: {stats[0]}</li>
            <li>Total AI Insights: {stats[1]}</li>
            <li>Total Venture Scores: {stats[2]}</li>
        </ul>

    </body>
    </html>
    """

    return html_content