# shared/modal_job_map.py — link Modal factory run id ↔ backend dubbing_jobs.id
import logging
import os
from typing import Any, Optional

import redis

from shared import config

logger = logging.getLogger(__name__)

_TTL_SECONDS = 48 * 3600


def _client():
    return redis.from_url(config.REDIS_URL, decode_responses=True)


def link_modal_to_backend(modal_job_id: str, backend_job_id: str) -> None:
    modal_job_id = (modal_job_id or "").strip()
    backend_job_id = (backend_job_id or "").strip()
    if not modal_job_id or not backend_job_id:
        return
    try:
        c = _client()
        c.setex(f"dub:modal:{modal_job_id}", _TTL_SECONDS, backend_job_id)
        c.setex(f"dub:backend_modal:{backend_job_id}", _TTL_SECONDS, modal_job_id)
        logger.info("Linked Modal job %s → backend %s", modal_job_id, backend_job_id)
    except Exception as exc:
        logger.warning("link_modal_to_backend failed: %s", exc)


def get_modal_job_id(backend_job_id: str) -> Optional[str]:
    key = (backend_job_id or "").strip()
    if not key:
        return None
    try:
        return (_client().get(f"dub:backend_modal:{key}") or "").strip() or None
    except Exception as exc:
        logger.warning("get_modal_job_id failed: %s", exc)
        return None


def extract_modal_ids_from_response(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []
    ids: list[str] = []
    for k in (
        "job_id", "id", "call_id", "modal_job_id", "run_id", "task_id",
        "request_id", "gateway_request_id",
    ):
        v = data.get(k)
        if v is not None and str(v).strip():
            ids.append(str(v).strip())
    nested = data.get("result") or data.get("data") or {}
    if isinstance(nested, dict):
        for k in ("job_id", "id", "call_id"):
            v = nested.get(k)
            if v is not None and str(v).strip():
                ids.append(str(v).strip())
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out
