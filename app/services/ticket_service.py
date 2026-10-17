from ..repositories import ticket_repo


def join(queue: dict, name: str) -> dict:
    ticket = ticket_repo.create(queue["id"], name)
    return _enrich(queue, ticket)


def position_and_eta(queue: dict, ticket: dict) -> tuple[int, int]:
    if ticket["status"] == "called":
        return 0, 0
    if ticket["status"] in ("served", "skipped"):
        return -1, 0
    waiting = ticket_repo.waiting(queue["id"])
    current = ticket_repo.current_called(queue["id"])
    ahead = sum(1 for t in waiting if t["number"] < ticket["number"])
    position = ahead + 1 if current else ahead
    return position, position * queue["avg_service_min"]


def _enrich(queue: dict, ticket: dict) -> dict:
    pos, eta = position_and_eta(queue, ticket)
    return {
        "ticket_id": ticket["id"],
        "number": ticket["number"],
        "name": ticket["name"],
        "status": ticket["status"],
        "position": pos,
        "eta_minutes": eta,
        "current_number": (ticket_repo.current_called(queue["id"]) or {}).get("number"),
    }


def status(queue: dict, ticket: dict) -> dict:
    return _enrich(queue, ticket)


def call_next(queue: dict) -> dict:
    result = ticket_repo.call_next(queue["id"])
    waiting = ticket_repo.waiting(queue["id"])
    return {
        "served": _safe(queue, result["served"]),
        "called": _safe(queue, result["called"]),
        "waiting_count": len(waiting),
    }


def _safe(queue, ticket):
    return _enrich(queue, ticket) if ticket else None


def queue_state(queue: dict) -> dict:
    current = ticket_repo.current_called(queue["id"])
    waiting = ticket_repo.waiting(queue["id"])
    return {
        "queue": {"id": queue["id"], "name": queue["name"],
                  "avg_service_min": queue["avg_service_min"]},
        "current": _safe(queue, current),
        "waiting": [_enrich(queue, t) for t in waiting],
        "stats": {"served_today": ticket_repo.served_today(queue["id"]),
                  "waiting_count": len(waiting)},
    }