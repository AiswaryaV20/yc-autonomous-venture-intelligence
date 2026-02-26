from db.database import SessionLocal
from sqlalchemy import text


def detect_snapshot_changes(company_id):
    session = SessionLocal()

    snapshots = session.execute(
        text("""
            SELECT raw_data
            FROM company_snapshots
            WHERE company_id = :cid
            ORDER BY scraped_at DESC
            LIMIT 2
        """),
        {"cid": company_id}
    ).fetchall()

    if len(snapshots) < 2:
        session.close()
        return None

    latest = snapshots[0][0]
    previous = snapshots[1][0]

    changes = []

    for key in latest:
        if key in previous and latest[key] != previous[key]:
            changes.append(
                f"{key} changed from '{previous[key]}' to '{latest[key]}'"
            )

    session.close()

    if changes:
        return "\n".join(changes)

    return None