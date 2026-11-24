import uuid

from gpu_compare.config import settings
from gpu_compare.db import transaction


def active_session(db, session):
    if not db.one("SELECT id FROM sessions WHERE id=:id AND expires_at>now()", {"id": session}):
        raise PermissionError("Die Demo-Sitzung ist abgelaufen. Bitte neu starten.")


def create_session():
    session = str(uuid.uuid4())
    # Advisory lock makes the demo's global admission limit atomic across Lambda instances.
    with transaction() as db:
        db.execute("SELECT pg_advisory_xact_lock(71823761) IS NULL AS locked")
        count = db.one(
            "SELECT count(*) AS count FROM sessions WHERE created_at>now()-interval '1 hour'"
        )
        if int(count["count"]) >= settings().max_sessions_per_hour:
            raise ValueError(
                "Die Demo ist gerade stark ausgelastet. Bitte später erneut versuchen."
            )
        from gpu_compare.benchmarks.service import scrub_sessions

        scrub_sessions(db)
        db.execute("DELETE FROM sessions WHERE expires_at<now()")
        db.execute("INSERT INTO sessions(id) VALUES (:id)", {"id": session})
    return session
