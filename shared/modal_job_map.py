# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/modal_job_map.py
# # AR Celery workers
# # KW مهمة,job,تنفيذ,local
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/modal_job_map.py
# # AR Celery workers
# # KW مهمة,job,تنفيذ,local
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/modal_job_map.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/modal_job_map.py — link Modal factory run id ↔ backend dubbing_jobs.id
import logging
import os
from typing import Any, Optional

import redis

from shared import config

logger = logging.getLogger(__name__)

_TTL_SECONDS = 48 * 3600


# # FN _client
# # AR client (_client)
# # FN _client
# # AR مهام المعالجة (_client)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN _client
# # AR مهام المعالجة (_client)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def _client():
    return redis.from_url(config.REDIS_URL, decode_responses=True)


# # FN link_modal_to_backend
# # AR link modal to backend (link_modal_to_backend)
# # FN link_modal_to_backend
# # AR مهام المعالجة (link_modal_to_backend)
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN link_modal_to_backend
# # AR مهام المعالجة (link_modal_to_backend)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def link_modal_to_backend(modal_job_id: str, backend_job_id: str) -> None:
    modal_job_id = (modal_job_id or "").strip()
    backend_job_id = (backend_job_id or "").strip()
    if not modal_job_id or not backend_job_id:
        # # return — إرجاع النتيجة
        return
    # # block — إرجاع نتيجة
    # # block — معالجة أخطاء
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        c = _client()
        # # block — معالجة أخطاء
        c.setex(f"dub:modal:{modal_job_id}", _TTL_SECONDS, backend_job_id)
        c.setex(f"dub:backend_modal:{backend_job_id}", _TTL_SECONDS, modal_job_id)
        # # block — معالجة أخطاء
        logger.info("Linked Modal job %s → backend %s", modal_job_id, backend_job_id)
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except Exception as exc:
        logger.warning("link_modal_to_backend failed: %s", exc)


# # FN get_modal_job_id
# # block — معالجة أخطاء
# # AR جلب modal job id (get_modal_job_id)
# # block — معالجة أخطاء
# # FN get_modal_job_id
# # AR مهام المعالجة (get_modal_job_id)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN get_modal_job_id
# # AR مهام المعالجة (get_modal_job_id)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def get_modal_job_id(backend_job_id: str) -> Optional[str]:
    key = (backend_job_id or "").strip()
    if not key:
        # # return — إرجاع النتيجة
        return None
    # # try — معالجة عملية قد تفشل
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        return (_client().get(f"dub:backend_modal:{key}") or "").strip() or None
    # # catch — التقاط الخطأ
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception as exc:
        # # block — معالجة أخطاء
        logger.warning("get_modal_job_id failed: %s", exc)
        # # return — إرجاع النتيجة
        # # block — معالجة أخطاء
        return None


# # FN extract_modal_ids_from_response
# # AR استخراج modal ids from response (extract_modal_ids_from_response)
# # FN extract_modal_ids_from_response
# # block — إرجاع نتيجة
# # AR مهام المعالجة (extract_modal_ids_from_response)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN extract_modal_ids_from_response
# # AR مهام المعالجة (extract_modal_ids_from_response)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def extract_modal_ids_from_response(data: Any) -> list[str]:
    if not isinstance(data, dict):
        # # return — إرجاع النتيجة
        return []
    ids: list[str] = []
    for k in (
        # # block — حلقة/تكرار
        # # block — حلقة/تكرار
        "job_id", "id", "call_id", "modal_job_id", "run_id", "task_id",
        "request_id", "gateway_request_id",
    ):
        v = data.get(k)
        if v is not None and str(v).strip():
            # # block — تنفيذ منطق — راجع الأسطر التالية
            ids.append(str(v).strip())
    # # block — تنفيذ منطق — راجع الأسطر التالية
    nested = data.get("result") or data.get("data") or {}
    if isinstance(nested, dict):
        for k in ("job_id", "id", "call_id"):
            v = nested.get(k)
            # # block — حلقة/تكرار
            if v is not None and str(v).strip():
                ids.append(str(v).strip())
    # # block — حلقة/تكرار
    seen = set()
    out = []
    for i in ids:
        # # block — حلقة/تكرار
        if i not in seen:
            seen.add(i)
            out.append(i)
    # # block — حلقة/تكرار
    # # return — إرجاع النتيجة
    return out
