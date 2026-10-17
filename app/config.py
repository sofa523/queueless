import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "./data/queueless.db")

# Создаём директорию под БД, если её нет
_os_dir = os.path.dirname(DATABASE_URL)
if _os_dir:
    os.makedirs(_os_dir, exist_ok=True)

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
_vapid_file = os.getenv("VAPID_PRIVATE_KEY_FILE", "")
if not VAPID_PRIVATE_KEY and _vapid_file and os.path.exists(_vapid_file):
    with open(_vapid_file, "r", encoding="utf-8") as f:
        VAPID_PRIVATE_KEY = f.read().strip()

VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@example.com")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

SLUG_LENGTH = 6
TOKEN_LENGTH = 32
NAME_MAX_LENGTH = 50
QUEUE_NAME_MAX_LENGTH = 100
AVG_SERVICE_MIN_DEFAULT = 15
AVG_SERVICE_MIN_MIN = 1
AVG_SERVICE_MIN_MAX = 120
POLLING_INTERVAL = 5
TICKET_TTL_HOURS = 24
RATE_LIMIT_JOIN = 10
QR_SIZE = 300