from fastapi import APIRouter, HTTPException
from ..repositories import queue_repo, ticket_repo, subscription_repo
from ..services import ticket_service
from ..schemas import TicketCreate, PushSubscribe

router = APIRouter(prefix="/api/queue", tags=["client"])


def _get_queue(slug: str) -> dict:
    q = queue_repo.get_by_slug(slug)
    if not q:
        raise HTTPException(404, detail={"error": {"code": "QUEUE_NOT_FOUND",
                                                   "message": "Очередь не найдена"}})
    if not q["is_active"]:
        raise HTTPException(409, detail={"error": {"code": "QUEUE_INACTIVE",
                                                   "message": "Очередь закрыта"}})
    return q


@router.post("/{slug}/join", status_code=201)
def join(slug: str, payload: TicketCreate):
    q = _get_queue(slug)
    return ticket_service.join(q, payload.name)


@router.get("/{slug}/ticket/{ticket_id}")
def status(slug: str, ticket_id: str):
    q = _get_queue(slug)
    t = ticket_repo.get_by_id(ticket_id)
    if not t or t["queue_id"] != q["id"]:
        raise HTTPException(404, detail={"error": {"code": "TICKET_NOT_FOUND",
                                                   "message": "Билет не найден"}})
    return ticket_service.status(q, t)


@router.post("/{slug}/ticket/{ticket_id}/subscribe", status_code=201)
def subscribe(slug: str, ticket_id: str, payload: PushSubscribe):
    q = _get_queue(slug)
    t = ticket_repo.get_by_id(ticket_id)
    if not t or t["queue_id"] != q["id"]:
        raise HTTPException(404, detail={"error": {"code": "TICKET_NOT_FOUND",
                                                   "message": "Билет не найден"}})
    sub = subscription_repo.create(
        ticket_id=ticket_id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.get("p256dh", ""),
        auth=payload.keys.get("auth", ""),
    )
    return {"subscription_id": sub["id"], "type": sub["type"]}