import os
import qrcode
from ..config import BASE_URL, QR_SIZE
from ..repositories import queue_repo

QR_DIR = "static/qr"


def create_queue(name: str, avg_service_min: int) -> dict:
    queue = queue_repo.create(name, avg_service_min)
    os.makedirs(QR_DIR, exist_ok=True)
    public_url = f"{BASE_URL}/q/{queue['public_slug']}"
    img = qrcode.make(public_url)
    img = img.resize((QR_SIZE, QR_SIZE))
    img.save(f"{QR_DIR}/{queue['public_slug']}.png")
    return {
        "queue_id": queue["id"],
        "admin_token": queue["admin_token"],
        "public_slug": queue["public_slug"],
        "admin_url": f"/admin/{queue['admin_token']}",
        "public_url": f"/q/{queue['public_slug']}",
        "qr_url": f"/static/qr/{queue['public_slug']}.png",
    }