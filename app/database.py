import sqlite3
from contextlib import contextmanager
from .config import DATABASE_URL

SCHEMA = """
CREATE TABLE IF NOT EXISTS queues (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    admin_token TEXT NOT NULL UNIQUE,
    public_slug TEXT NOT NULL UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1,
    avg_service_min INTEGER NOT NULL DEFAULT 15,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    queue_id TEXT NOT NULL REFERENCES queues(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    number INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'waiting',
    created_at TEXT NOT NULL,
    called_at TEXT,
    served_at TEXT,
    skipped_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tickets_queue_status
    ON tickets(queue_id, status, number);

CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    type TEXT NOT NULL DEFAULT 'webpush',
    endpoint TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def init_db() -> None:
    conn = sqlite3.connect(DATABASE_URL)
    try:
        conn.executescript(SCHEMA)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_URL, isolation_level=None, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
    finally:
        conn.close()