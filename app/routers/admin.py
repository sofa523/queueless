from fastapi import APIRouter, HTTPException, Depends
from ..repositories import queue_repo, ticket_repo
from ..services import ticket_service
from ..schemas import QueueCreate, TicketCreate

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_queue_by_token(token: str) -> dict:
    q = queue_repo.get_by_token(token)
    if not q:
        raise HTTPException(403, detail={"error": {"code": "INVALID_TOKEN",
                                                   "message": "Неверный токен"}})
    return q


@router.post("/queues", status_code=201)
def create_queue(payload: QueueCreate):
    from ..services.queue_service import create_queue
    return create_queue(payload.name, payload.avg_service_min)


@router.get("/queues/{token}/state")
def state(token: str):
    q = get_queue_by_token(token)
    return ticket_service.queue_state(q)


@router.post("/queues/{token}/next")
def next_client(token: str):
    q = get_queue_by_token(token)
    result = ticket_service.call_next(q)
    if result["called"]:
        from ..services.notify_service import send_to_ticket
        send_to_ticket(result["called"]["ticket_id"], {
            "title": "Ваша очередь!",
            "body": f"Подойдите к стойке. Номер {result['called']['number']}",
        })
    return result


@router.post("/queues/{token}/tickets", status_code=201)
def add_ticket(token: str, payload: TicketCreate):
    q = get_queue_by_token(token)
    return ticket_service.join(q, payload.name)


@router.post("/queues/{token}/tickets/{ticket_id}/skip")
def skip(token: str, ticket_id: str):
    q = get_queue_by_token(token)
    t = ticket_repo.get_by_id(ticket_id)
    if not t or t["queue_id"] != q["id"]:
        raise HTTPException(404, detail={"error": {"code": "TICKET_NOT_FOUND",
                                                   "message": "Билет не найден"}})
    t = ticket_repo.set_status(ticket_id, "skipped", "skipped_at")
    return ticket_service._enrich(q, t)


@router.post("/queues/{token}/tickets/{ticket_id}/serve")
def serve(token: str, ticket_id: str):
    q = get_queue_by_token(token)
    t = ticket_repo.get_by_id(ticket_id)
    if not t or t["queue_id"] != q["id"]:
        raise HTTPException(404, detail={"error": {"code": "TICKET_NOT_FOUND",
                                                   "message": "Билет не найден"}})
    t = ticket_repo.set_status(ticket_id, "served", "served_at")
    return ticket_service._enrich(q, t)