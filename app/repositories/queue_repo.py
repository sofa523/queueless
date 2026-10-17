import uuid
import secrets
import string
from datetime import datetime, timezone
from ..database import get_conn
from ..config import TOKEN_LENGTH, SLUG_LENGTH

_ALPHABET = string.ascii_letters + string.digits


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_token() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(TOKEN_LENGTH))


def _gen_slug() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(SLUG_LENGTH))


def create(name: str, avg_service_min: int) -> dict:
    qid = str(uuid.uuid4())
    with get_conn() as conn:
        for _ in range(10):
            token = _gen_token()
            slug = _gen_slug()
            try:
                conn.execute(
                    "INSERT INTO queues (id, name, admin_token, public_slug, "
                    "is_active, avg_service_min, created_at) VALUES (?,?,?,?,1,?,?)",
                    (qid, name, token, slug, avg_service_min, _now()),
                )
                return get_by_id(qid)
            except Exception:
                continue
        raise RuntimeError("Не удалось создать очередь")


def get_by_id(qid: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM queues WHERE id=?", (qid,)).fetchone()
        return dict(row) if row else None


def get_by_token(token: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM queues WHERE admin_token=?", (token,)).fetchone()
        return dict(row) if row else None


def get_by_slug(slug: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM queues WHERE public_slug=?", (slug,)).fetchone()
        return dict(row) if row else None