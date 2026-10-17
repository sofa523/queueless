import uuid
from datetime import datetime, timezone
from ..database import get_conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create(ticket_id: str, endpoint: str, p256dh: str, auth: str, type_: str = "webpush") -> dict:
    sid = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO subscriptions (id, ticket_id, type, endpoint, p256dh, auth, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (sid, ticket_id, type_, endpoint, p256dh, auth, _now()),
        )
        row = conn.execute("SELECT * FROM subscriptions WHERE id=?", (sid,)).fetchone()
        return dict(row)


def list_for_ticket(ticket_id: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM subscriptions WHERE ticket_id=?", (ticket_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete(sid: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM subscriptions WHERE id=?", (sid,))