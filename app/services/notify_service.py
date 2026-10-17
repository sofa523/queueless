import json
from ..config import VAPID_PRIVATE_KEY, VAPID_SUBJECT
from ..repositories import subscription_repo

try:
    from pywebpush import webpush, WebPushException
    HAS_WEBPUSH = True
except Exception:
    HAS_WEBPUSH = False


def send_to_ticket(ticket_id: str, payload: dict) -> int:
    if not HAS_WEBPUSH or not VAPID_PRIVATE_KEY:
        return 0
    sent = 0
    for sub in subscription_repo.list_for_ticket(ticket_id):
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
                },
                data=json.dumps(payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_SUBJECT},
            )
            sent += 1
        except WebPushException as e:
            # 404/410 — подписка невалидна → удаляем
            if getattr(e, "response", None) and e.response.status_code in (404, 410):
                subscription_repo.delete(sub["id"])
    return sent