from db.database import SessionLocal
from db.models import Company
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=5):

    session = SessionLocal()

    query_embedding = model.encode(query)

    rows = session.execute(
        text("SELECT company_id, embedding FROM company_embeddings")
    ).fetchall()

    similarities = []

    for row in rows:
        company_id = row[0]
        embedding = np.array(row[1])

        score = np.dot(query_embedding, embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
        )

        similarities.append((company_id, score))

    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    top_ids = [x[0] for x in similarities[:top_k]]

    companies = session.query(Company).filter(Company.id.in_(top_ids)).all()

    session.close()

    return companies