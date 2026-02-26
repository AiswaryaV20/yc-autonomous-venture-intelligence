from db.database import SessionLocal
from db.models import Company, CompanySnapshot
from scraper.yc_scraper import scrape_all_companies
import hashlib
import json


def generate_hash(data):
    cleaned = json.dumps(data, sort_keys=True)
    return hashlib.sha256(cleaned.encode()).hexdigest()


def run_scraper():
    session = SessionLocal()

    companies = scrape_all_companies()

    print("Fetched:", len(companies))

    for comp in companies:
        yc_id = comp["profile_link"]  # using link as unique ID
        snapshot_hash = generate_hash(comp)

        existing = session.query(Company).filter_by(
            yc_company_id=yc_id
        ).first()

        if not existing:
            new_company = Company(
                yc_company_id=yc_id,
                name=comp["name"],
                domain=comp["profile_link"],
                is_active=True
            )
            session.add(new_company)
            session.commit()

            snapshot = CompanySnapshot(
                company_id=new_company.id,
                raw_data=comp,
                snapshot_hash=snapshot_hash
            )
            session.add(snapshot)

        else:
            latest_snapshot = session.query(CompanySnapshot)\
                .filter_by(company_id=existing.id)\
                .order_by(CompanySnapshot.scraped_at.desc())\
                .first()

            if latest_snapshot.snapshot_hash != snapshot_hash:
                snapshot = CompanySnapshot(
                    company_id=existing.id,
                    raw_data=comp,
                    snapshot_hash=snapshot_hash
                )
                session.add(snapshot)

        session.commit()

    session.close()
    print("Done inserting data.")


if __name__ == "__main__":
    run_scraper()