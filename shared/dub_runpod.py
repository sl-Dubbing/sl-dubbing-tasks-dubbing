# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_runpod.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_runpod.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_runpod.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/dub_runpod.py — RunPod sync polling for dubbing
from __future__ import annotations

import time

import requests

from shared import config


# # FN is_runpod_backend_url
# # AR هل runpod backend url (is_runpod_backend_url)
# # FN is_runpod_backend_url
# # AR دالة is_runpod_backend_url (is_runpod_backend_url)
# # KW عام,general
# # FN is_runpod_backend_url
# # AR دالة is_runpod_backend_url (is_runpod_backend_url)
# # KW عام,general
def is_runpod_backend_url(backend_url: str) -> bool:
    url = (backend_url or "").lower()
    # # return — إرجاع النتيجة
    return "runpod.ai" in url or "runpod.io" in url


# # FN poll_runpod_until_output
# # AR استطلاع runpod until output (poll_runpod_until_output)
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # FN poll_runpod_until_output
# # AR مهام المعالجة (poll_runpod_until_output)
# # KW مهمة,job,polling,celery,worker
# # FN poll_runpod_until_output
# # AR مهام المعالجة (poll_runpod_until_output)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker
def poll_runpod_until_output(backend_url: str, payload: dict, timeout: int = 1500) -> dict:
    headers = {
        "Authorization": f"Bearer {config.RUNPOD_API_KEY}",
        "Content-Type": "application/json",
    }
    base = backend_url.rstrip("/")
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # HTTP — طلب outbound
    # # HTTP — outbound
    # # HTTP — outbound
    run_resp = requests.post(
        f"{base}/run",
        # # block — طلب HTTP/API
        json={"input": payload},
        headers=headers,
        # # block — طلب HTTP/API
        timeout=60,
    )
    run_resp.raise_for_status()
    # # block — معالجة أخطاء
    # # parse — قراءة JSON من الاستجابة
    runpod_job_id = run_resp.json().get("id")
    deadline = time.time() + timeout

    # # block — parse/serialize JSON
    while time.time() < deadline:
        # # HTTP — طلب outbound
        # # block — parse/serialize JSON
        # # HTTP — outbound
        # # HTTP — outbound
        status_data = requests.get(
            f"{base}/status/{runpod_job_id}",
            headers=headers,
            # # block — طلب HTTP/API
            # # block — طلب HTTP/API
            timeout=30,
        # # parse — قراءة JSON من الاستجابة
        ).json()
        status = status_data.get("status")
        if status == "COMPLETED":
            # # return — إرجاع النتيجة
            # # block — parse/serialize JSON
            # # block — parse/serialize JSON
            return status_data.get("output") or {}
        if status in ("FAILED", "CANCELLED"):
            # # raise — رفع خطأ للم caller
            raise RuntimeError(f"RunPod failed: {status_data.get('error')}")
        time.sleep(5)
    # # block — معالجة أخطاء
    # # raise — رفع خطأ للم caller
    # # block — معالجة أخطاء
    raise TimeoutError("RunPod dubbing timed out")
