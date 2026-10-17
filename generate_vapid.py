# generate_vapid.py
import base64
from pathlib import Path

from py_vapid import Vapid
from cryptography.hazmat.primitives import serialization


def main() -> None:
    v = Vapid()
    v.generate_keys()

    # --- Приватный ключ в PEM ---
    private_pem = v.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # --- Публичный ключ в URL-safe base64 (65 байт, uncompressed point) ---
    public_raw = v.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    public_key = base64.urlsafe_b64encode(public_raw).rstrip(b"=").decode("ascii")

    # --- Сохраняем приватный ключ в файл ---
    Path("private_key.pem").write_text(private_pem, encoding="utf-8")

    # --- Обновляем .env ---
    env_path = Path(".env")
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []

    keys_to_set = {
        "VAPID_PRIVATE_KEY_FILE": "private_key.pem",
        "VAPID_PUBLIC_KEY": public_key,
        "VAPID_SUBJECT": "mailto:admin@example.com",
    }

    updated, seen = [], set()
    for line in lines:
        if "=" in line:
            k = line.split("=", 1)[0].strip()
            if k in keys_to_set:
                updated.append(f"{k}={keys_to_set[k]}")
                seen.add(k)
                continue
        updated.append(line)
    for k, val in keys_to_set.items():
        if k not in seen:
            updated.append(f"{k}={val}")

    env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")

    print("Приватный ключ: private_key.pem")
    print(".env обновлён")
    print()
    print("VAPID_PUBLIC_KEY:")
    print(public_key)
    print()
    print("Вставьте в static/client.html:")
    print(f'<script>window.VAPID_PUBLIC_KEY = "{public_key}";</script>')


if __name__ == "__main__":
    main()