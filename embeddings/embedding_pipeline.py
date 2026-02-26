from db.database import SessionLocal
from db.models import Company
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import numpy as np

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def build_embeddings():
    session = SessionLocal()

    companies = session.query(Company).all()

    if not companies:
        print("No companies found.")
        return

    print(f"Building embeddings for {len(companies)} companies...")

    # Clear old embeddings (important)
    session.execute(text("DELETE FROM company_embeddings"))
    session.commit()

    for company in companies:

        text_input = f"{company.name} {company.domain or ''}"

        embedding = model.encode(text_input)

        session.execute(
            text("""
                INSERT INTO company_embeddings
                (company_id, embedding, source_type)
                VALUES (:company_id, :embedding, :source)
            """),
            {
                "company_id": company.id,
                "embedding": embedding.tolist(),
                "source": "description"
            }
        )

    session.commit()
    session.close()

    print("Embeddings stored successfully.")


if __name__ == "__main__":
    build_embeddings()