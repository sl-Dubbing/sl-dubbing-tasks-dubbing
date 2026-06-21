# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/security.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/security.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/security.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/security.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/security.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/security.py — Celery worker helpers (mirrors sl-dubbing-backend-main/shared/security.py)
from __future__ import annotations

import os


# # FN inference_request_headers
# # AR inference request headers (inference_request_headers)
# # FN inference_request_headers
# # AR دالة inference_request_headers (inference_request_headers)
# # KW عام,general
# # FN inference_request_headers
# # AR دالة inference_request_headers (inference_request_headers)
# # KW عام,general
# # FN inference_request_headers
# # AR دالة inference_request_headers (inference_request_headers)
# # KW عام,general
# # FN inference_request_headers
# # AR دالة inference_request_headers (inference_request_headers)
# # KW عام,general
def inference_request_headers() -> dict:
    """Headers for Celery → GPU worker calls (upload-from-url, clean-cache, …)."""
    headers: dict = {"Content-Type": "application/json"}
    mode = (os.environ.get("EXECUTION_MODE") or "").strip().lower()
    if mode == "local":
        secret_names = ("WEBHOOK_SECRET", "MODAL_WEBHOOK_SECRET", "MODAL_TOKEN_SECRET")
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    else:
        secret_names = ("MODAL_TOKEN_SECRET", "MODAL_WEBHOOK_SECRET", "WEBHOOK_SECRET")
    for name in secret_names:
        val = (os.environ.get(name) or "").strip()
        if val:
            # # block — حلقة/تكرار
            headers["Authorization"] = f"Bearer {val}"
            # # block — حلقة/تكرار
            headers["X-Webhook-Secret"] = val
            break
    return headers
