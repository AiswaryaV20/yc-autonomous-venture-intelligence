from db.database import SessionLocal
from db.models import Company


def search(query: str, top_k: int = 5):
    """
    Lightweight fallback search for deployment.
    Returns top_k companies based on simple text matching.
    """

    session = SessionLocal()

    try:
        # Basic case-insensitive filtering using name or domain
        companies = (
            session.query(Company)
            .filter(
                (Company.name.ilike(f"%{query}%")) |
                (Company.domain.ilike(f"%{query}%"))
            )
            .limit(top_k)
            .all()
        )

        # If no match found, just return first top_k companies
        if not companies:
            companies = session.query(Company).limit(top_k).all()

        return companies

    finally:
        session.close()