import uuid
from datetime import datetime, timezone
from ..database import get_conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create(queue_id: str, name: str) -> dict:
    tid = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                "SELECT COALESCE(MAX(number),0) AS n FROM tickets WHERE queue_id=?",
                (queue_id,),
            ).fetchone()
            number = row["n"] + 1
            conn.execute(
                "INSERT INTO tickets (id, queue_id, name, number, status, created_at) "
                "VALUES (?,?,?,?, 'waiting', ?)",
                (tid, queue_id, name, number, _now()),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return get_by_id(tid)


def get_by_id(tid: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone()
        return dict(row) if row else None


def waiting(queue_id: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE queue_id=? AND status='waiting' ORDER BY number",
            (queue_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def current_called(queue_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE queue_id=? AND status='called' "
            "ORDER BY called_at DESC LIMIT 1",
            (queue_id,),
        ).fetchone()
        return dict(row) if row else None


def served_today(queue_id: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM tickets WHERE queue_id=? AND status='served' "
            "AND date(served_at)=date('now')",
            (queue_id,),
        ).fetchone()
        return row["c"]


def set_status(tid: str, status: str, ts_field: str) -> dict:
    with get_conn() as conn:
        conn.execute(
            f"UPDATE tickets SET status=?, {ts_field}=? WHERE id=?",
            (status, _now(), tid),
        )
    return get_by_id(tid)


def call_next(queue_id: str) -> dict:
    """Атомарно: текущий called → served, первый waiting → called."""
    with get_conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            called = conn.execute(
                "SELECT * FROM tickets WHERE queue_id=? AND status='called' "
                "ORDER BY called_at DESC LIMIT 1",
                (queue_id,),
            ).fetchone()
            if called:
                conn.execute(
                    "UPDATE tickets SET status='served', served_at=? WHERE id=?",
                    (_now(), called["id"]),
                )
            nxt = conn.execute(
                "SELECT * FROM tickets WHERE queue_id=? AND status='waiting' "
                "ORDER BY number LIMIT 1",
                (queue_id,),
            ).fetchone()
            if not nxt:
                conn.execute("COMMIT")
                return {"served": dict(called) if called else None, "called": None}
            conn.execute(
                "UPDATE tickets SET status='called', called_at=? WHERE id=?",
                (_now(), nxt["id"]),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return {
        "served": get_by_id(called["id"]) if called else None,
        "called": get_by_id(nxt["id"]),
    }


def cleanup_expired(ttl_hours: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM tickets WHERE status IN ('served','skipped') "
            "AND datetime(COALESCE(served_at, skipped_at)) < datetime('now', ?)",
            (f"-{ttl_hours} hours",),
        )
        return cur.rowcount