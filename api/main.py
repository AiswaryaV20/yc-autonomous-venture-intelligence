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
        # 1️⃣ Semantic search
        results = search(request.question, top_k=5)

        if not results:
            return {
                "question": request.question,
                "answer": "No relevant companies found.",
                "cited_companies": [],
                "reasoning_trace": [],
                "confidence": 0.2
            }

        context_blocks = []
        cited_companies = []

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

                context_blocks.append(
                    f"Company: {company.name}\nInsight: {insight[0]}"
                )

        context_text = "\n\n".join(context_blocks)

        # 2️⃣ LLM reasoning synthesis (LOCAL MODEL)
        from services.llm_service import generate_completion

        prompt = f"""
You are an AI Venture Intelligence Analyst.

Question:
{request.question}

Relevant Company Insights:
{context_text}

Instructions:
- Answer analytically.
- Cite companies explicitly.
- Explain reasoning clearly.
- Provide a confidence score (0-1).
        """

        ai_response = generate_completion(prompt)

        return {
            "question": request.question,
            "answer": ai_response,
            "cited_companies": cited_companies,
            "reasoning_trace": [
                "Semantic embedding retrieval",
                "Insight-based synthesis",
                "LLM analytical reasoning"
            ],
            "confidence": 0.85
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        session.close()
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