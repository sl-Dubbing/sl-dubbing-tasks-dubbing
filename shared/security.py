# shared/security.py — Celery worker helpers (mirrors sl-dubbing-backend-main/shared/security.py)
from __future__ import annotations

import os


def inference_request_headers() -> dict:
    """Headers for Celery → GPU worker calls (upload-from-url, clean-cache, …)."""
    headers: dict = {"Content-Type": "application/json"}
    for name in ("MODAL_TOKEN_SECRET", "MODAL_WEBHOOK_SECRET", "WEBHOOK_SECRET"):
        val = (os.environ.get(name) or "").strip()
        if val:
            headers["Authorization"] = f"Bearer {val}"
            headers["X-Webhook-Secret"] = val
            break
    return headers
