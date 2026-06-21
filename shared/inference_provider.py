# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/inference_provider.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/inference_provider.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/inference_provider.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/inference_provider.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/inference_provider.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/inference_provider.py — Modal inference routing (مزامن مع sl-dubbing-backend-main)
# =====================================================================
#  #IP-04 trigger_modal_dubbing — إعادة محاولة + تحمّل cold start (لا يفشل عند timeout)
# =====================================================================
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

PROVIDER_MODAL = "modal"


class InferenceProviderError(Exception):
    """Misconfiguration or upstream inference failure."""


# # FN get_inference_provider
# # AR جلب inference provider (get_inference_provider)
# # FN get_inference_provider
# # AR دالة get_inference_provider (get_inference_provider)
# # KW عام,general
# # FN get_inference_provider
# # AR دالة get_inference_provider (get_inference_provider)
# # KW عام,general
# # FN get_inference_provider
# # AR دالة get_inference_provider (get_inference_provider)
# # KW عام,general
# # FN get_inference_provider
# # AR دالة get_inference_provider (get_inference_provider)
# # KW عام,general
def get_inference_provider() -> str:
    # # return — إرجاع النتيجة
    return PROVIDER_MODAL


# # FN get_active_inference_provider
# # AR جلب active inference provider (get_active_inference_provider)
# # FN get_active_inference_provider
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR دالة get_active_inference_provider (get_active_inference_provider)
# # KW عام,general
# # FN get_active_inference_provider
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة get_active_inference_provider (get_active_inference_provider)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN get_active_inference_provider
# # AR دالة get_active_inference_provider (get_active_inference_provider)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_active_inference_provider
# # AR دالة get_active_inference_provider (get_active_inference_provider)
# # KW عام,general
def get_active_inference_provider() -> str:
    # # return — إرجاع النتيجة
    return PROVIDER_MODAL


# # FN _int_env
# # AR int env (_int_env)
# # FN _int_env
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR دالة _int_env (_int_env)
# # KW عام,general
# # FN _int_env
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة _int_env (_int_env)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN _int_env
# # AR دالة _int_env (_int_env)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _int_env
# # AR دالة _int_env (_int_env)
# # KW عام,general
def _int_env(name: str, default: int) -> int:
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    try:
        # # block — معالجة أخطاء
        # # return — إرجاع النتيجة
        # # block — معالجة أخطاء
        return int(os.environ.get(name, default))
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except (TypeError, ValueError):
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # return — إرجاع النتيجة
        return default


_MODAL_DUB_CONNECT_TIMEOUT = _int_env("MODAL_DUB_CONNECT_TIMEOUT", 10)
# # block — معالجة أخطاء
# # block — معالجة أخطاء
_MODAL_DUB_READ_TIMEOUT = _int_env("MODAL_DUB_READ_TIMEOUT", 120)
# # block — إرجاع نتيجة
_MODAL_PAYLOAD_VERSION = "v2-normalize"


# # block — إرجاع نتيجة
# # FN _normalize_modal_dub_payload
# # AR تطبيع modal dub payload (_normalize_modal_dub_payload)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _normalize_modal_dub_payload
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (_normalize_modal_dub_payload)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW تنفيذ,local,cloud,modal,parity
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _normalize_modal_dub_payload
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (_normalize_modal_dub_payload)
# # KW تنفيذ,local,cloud,modal,parity
# # FN _normalize_modal_dub_payload
# # AR Local/Cloud parity (_normalize_modal_dub_payload)
# # KW تنفيذ,local,cloud,modal,parity
# # FN _normalize_modal_dub_payload
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (_normalize_modal_dub_payload)
# # KW تنفيذ,local,cloud,modal,parity
def _normalize_modal_dub_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(payload or {})
    raw_vc = p.get("voice_config") or p.get("voice") or {}
    vc = dict(raw_vc) if isinstance(raw_vc, dict) else {}

    top_sample = (
        p.get("sample_url") or p.get("sample_file") or p.get("voice_url") or p.get("url") or ""
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    ).strip()
    inner_sample = (
        vc.get("sample_url") or vc.get("sample_file") or vc.get("url") or vc.get("voice_url") or ""
    # # block — معالجة صوت/استنساخ
    ).strip()
    # # block — معالجة صوت/استنساخ
    sample = top_sample or inner_sample

    # # block — معالجة صوت/استنساخ
    if sample:
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        p["sample_url"] = sample
        p["sample_file"] = sample
        # # block — معالجة صوت/استنساخ
        if not (vc.get("sample_url") or vc.get("sample_file") or "").strip():
            vc["sample_url"] = sample
            # # block — معالجة صوت/استنساخ
            # # block — معالجة صوت/استنساخ
            vc["sample_file"] = sample

    sample_text = (p.get("sample_text") or vc.get("sample_text") or "").strip()
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    if sample_text:
        vc["sample_text"] = sample_text

    # # block — معالجة صوت/استنساخ
    p["voice_config"] = vc
    # # block — معالجة صوت/استنساخ
    # # return — إرجاع النتيجة
    return p


# # block — معالجة صوت/استنساخ
# # FN trigger_modal_dubbing
# # block — إرجاع نتيجة
# # block — معالجة صوت/استنساخ
# # AR trigger modal dubbing (trigger_modal_dubbing)
# # FN trigger_modal_dubbing
# # block — إرجاع نتيجة
# # AR Local/Cloud parity (trigger_modal_dubbing)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_dubbing
# # AR Local/Cloud parity (trigger_modal_dubbing)
# # KW تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_dubbing
# # AR Local/Cloud parity (trigger_modal_dubbing)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_dubbing
# # AR Local/Cloud parity (trigger_modal_dubbing)
# # KW تنفيذ,local,cloud,modal,parity
def trigger_modal_dubbing(payload: Dict[str, Any], timeout=None) -> Dict[str, Any]:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip().rstrip("/")
    if not modal_url:
        # # raise — رفع خطأ للم caller
        raise InferenceProviderError("MODAL_DUBBING_URL environment variable is not set")
    if timeout is None:
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        timeout = (_MODAL_DUB_CONNECT_TIMEOUT, _MODAL_DUB_READ_TIMEOUT)
    upload_url = f"{modal_url}/upload-from-url"
    headers = {"Content-Type": "application/json"}
    # # block — رفع أو تخزين ملف
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    # # block — رفع أو تخزين ملف
    if secret:
        # # block — رفع أو تخزين ملف
        headers["Authorization"] = f"Bearer {secret}"
    # # block — رفع أو تخزين ملف
    # # block — تنفيذ منطق — راجع الأسطر التالية
    payload = _normalize_modal_dub_payload(payload)
    vc = payload.get("voice_config") if isinstance(payload.get("voice_config"), dict) else {}
    # # block — معالجة صوت/استنساخ
    logger.info(
        "Payload to Modal (%s): job_id=%s lang=%s sample_url=%r voice_config.sample_url=%r keys=%s",
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        _MODAL_PAYLOAD_VERSION,
        payload.get("job_id"),
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        payload.get("lang"),
        (payload.get("sample_url") or "").strip(),
        # # block — معالجة صوت/استنساخ
        (vc.get("sample_url") or "").strip(),
        # # block — معالجة صوت/استنساخ
        sorted(payload.keys()),
    )

    # # block — معالجة صوت/استنساخ
    last_exc = None
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — معالجة صوت/استنساخ
    for attempt in range(1, 4):
        # # try — معالجة عملية قد تفشل
        # # block — معالجة أخطاء
        # # try — عملية قد تفشل
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # try — عملية قد تفشل
        # # try — عملية قد تفشل
        # # try — عملية قد تفشل
        try:
            # # HTTP — طلب outbound
            # # HTTP — outbound
            # # block — معالجة أخطاء
            # # block — طلب HTTP/API
            # # block — معالجة أخطاء
            # # block — معالجة أخطاء
            # # HTTP — outbound
            # # HTTP — outbound
            # # HTTP — outbound
            # # block — طلب HTTP/API
            r = requests.post(upload_url, json=payload, headers=headers, timeout=timeout)
            if r.status_code >= 500:
                logger.warning("Modal returned %s (attempt %s/3), retrying...", r.status_code, attempt)
                # # block — طلب HTTP/API
                last_exc = InferenceProviderError(f"Modal {r.status_code}")
                time.sleep(3 * attempt)
                # # block — معالجة أخطاء
                # # block — طلب HTTP/API
                continue
            # # block — معالجة أخطاء
            r.raise_for_status()
            # # block — معالجة أخطاء
            # # parse — قراءة JSON من الاستجابة
            # # block — parse/serialize JSON
            data = r.json()
            if isinstance(data, dict):
                # # block — parse/serialize JSON
                data.setdefault("provider", PROVIDER_MODAL)
            # # return — إرجاع النتيجة
            # # block — parse/serialize JSON
            # # block — إرجاع نتيجة
            # # block — parse/serialize JSON
            return data

        # # catch — التقاط الخطأ
        # # catch — التقاط خطأ
        # # block — معالجة أخطاء
        # # catch — التقاط خطأ
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            logger.warning(
                # # block — طلب HTTP/API
                "Modal cold-start/timeout (attempt %s/3): %s — retrying...",
                # # block — طلب HTTP/API
                # # block — معالجة أخطاء
                # # block — معالجة أخطاء
                attempt,
                exc,
            )
            time.sleep(5 * attempt)

        # # catch — التقاط الخطأ
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # catch — التقاط خطأ
        # # catch — التقاط خطأ
        except requests.exceptions.RequestException as exc:
            # # block — طلب HTTP/API
            last_exc = exc
            logger.warning("Modal request failed (attempt %s/3): %s", attempt, exc)
            # # block — طلب HTTP/API
            time.sleep(3 * attempt)

    # # block — طلب HTTP/API
    logger.warning(
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — طلب HTTP/API
        "Modal did not confirm within retries (job_id=%s): %s — "
        "assuming spawned; webhook is source of truth",
        # # block — تنفيذ منطق — راجع الأسطر التالية
        payload.get("job_id"),
        last_exc,
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    )
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    return {
        # # block — إرجاع نتيجة
        "success": True,
        "status": "processing",
        # # block — إرجاع نتيجة
        "spawned_unconfirmed": True,
        "job_id": payload.get("job_id"),
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — تنفيذ منطق — راجع الأسطر التالية
        "provider": PROVIDER_MODAL,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        "warning": f"Modal did not confirm in time: {last_exc}",
    }


# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN trigger_dubbing_job
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR trigger dubbing job (trigger_dubbing_job)
# # FN trigger_dubbing_job
# # AR مهام المعالجة (trigger_dubbing_job)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker
# # block — enqueue Celery
# # block — enqueue Celery
# # block — enqueue Celery
# # FN trigger_dubbing_job
# # AR مهام المعالجة (trigger_dubbing_job)
# # KW مهمة,job,polling,celery,worker
# # FN trigger_dubbing_job
# # block — enqueue Celery
# # AR مهام المعالجة (trigger_dubbing_job)
# # KW مهمة,job,polling,celery,worker
# # FN trigger_dubbing_job
# # AR مهام المعالجة (trigger_dubbing_job)
# # KW مهمة,job,polling,celery,worker
def trigger_dubbing_job(payload: Dict[str, Any], timeout=None) -> Dict[str, Any]:
    # # return — إرجاع النتيجة
    return trigger_modal_dubbing(payload, timeout=timeout)


# # FN trigger_modal_cancel
# # AR trigger modal cancel (trigger_modal_cancel)
# # FN trigger_modal_cancel
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR Local/Cloud parity (trigger_modal_cancel)
# # KW تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_cancel
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (trigger_modal_cancel)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_cancel
# # AR Local/Cloud parity (trigger_modal_cancel)
# # KW تنفيذ,local,cloud,modal,parity
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN trigger_modal_cancel
# # AR Local/Cloud parity (trigger_modal_cancel)
# # KW تنفيذ,local,cloud,modal,parity
def trigger_modal_cancel(job_id: str, timeout: int = 10) -> Dict[str, Any]:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip().rstrip("/")
    if not modal_url:
        # # raise — رفع خطأ للم caller
        raise InferenceProviderError("MODAL_DUBBING_URL environment variable is not set")

    cancel_url = f"{modal_url}/cancel"
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        # # block — تنفيذ منطق — راجع الأسطر التالية
        headers["Authorization"] = f"Bearer {secret}"

    # # block — تنفيذ منطق — راجع الأسطر التالية
    payload = {"job_id": (job_id or "").strip()}
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # HTTP — طلب outbound
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # HTTP — outbound
    # # HTTP — outbound
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # HTTP — outbound
    # # HTTP — outbound
    r = requests.post(cancel_url, json=payload, headers=headers, timeout=timeout)
    # # block — طلب HTTP/API
    r.raise_for_status()
    # # block — طلب HTTP/API
    # # parse — قراءة JSON من الاستجابة
    data = r.json()
    # # block — طلب HTTP/API
    return data if isinstance(data, dict) else {"success": True}


# # block — parse/serialize JSON
# # block — طلب HTTP/API
# # FN trigger_modal_tts
# # AR trigger modal tts (trigger_modal_tts)
# # block — توليد صوت TTS
# # FN trigger_modal_tts
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # AR Text-to-speech (trigger_modal_tts)
# # KW توليد_صوت,TTS,synthesis,تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_tts
# # AR Text-to-speech (trigger_modal_tts)
# # KW توليد_صوت,TTS,synthesis,تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_tts
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # AR Text-to-speech (trigger_modal_tts)
# # KW توليد_صوت,TTS,synthesis,تنفيذ,local,cloud,modal,parity
# # FN trigger_modal_tts
# # AR Text-to-speech (trigger_modal_tts)
# # KW توليد_صوت,TTS,synthesis,تنفيذ,local,cloud,modal,parity
def trigger_modal_tts(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    sample_url: Optional[str] = None,
    sample_text: str = "",
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    dialect: str = "",
    timeout: int = 180,
) -> Dict[str, Any]:
    # # block — توليد صوت TTS
    modal_tts_url = (os.environ.get("MODAL_TTS_URL") or "").strip().rstrip("/")
    # # block — توليد صوت TTS
    if not modal_tts_url:
        # # block — توليد صوت TTS
        raise InferenceProviderError("MODAL_TTS_URL is not set for Modal TTS inference")

    # # block — توليد صوت TTS
    # # block — توليد صوت TTS
    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    # # block — توليد صوت TTS
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    # # block — توليد صوت TTS
    # # block — توليد صوت TTS
    body: Dict[str, Any] = {
        "text": text,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — توليد صوت TTS
        "lang": lang,
        "lang_code": lang,
        # # block — معالجة صوت/استنساخ
        "voice_id": voice_id,
        # # block — معالجة صوت/استنساخ
        "sample_url": sample_url,
    }
    # # block — معالجة صوت/استنساخ
    if sample_text:
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        body["sample_text"] = sample_text
    if dialect:
        # # block — معالجة صوت/استنساخ
        body["dialect"] = dialect
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # HTTP — outbound
    # # HTTP — outbound
    # # HTTP — outbound
    # # HTTP — outbound
    r = requests.post(f"{modal_tts_url}/synthesize", json=body, headers=headers, timeout=timeout)
    r.raise_for_status()
    # # block — طلب HTTP/API
    # # block — طلب HTTP/API
    # # block — طلب HTTP/API
    # # block — طلب HTTP/API
    data = r.json()
    if isinstance(data, dict):
        data.setdefault("provider", PROVIDER_MODAL)
    # # block — parse/serialize JSON
    return data


# # FN trigger_tts_inference
# # block — توليد صوت TTS
# # AR trigger tts inference (trigger_tts_inference)
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # FN trigger_tts_inference
# # AR Text-to-speech (trigger_tts_inference)
# # KW توليد_صوت,TTS,synthesis
# # block — توليد صوت TTS
# # FN trigger_tts_inference
# # AR Text-to-speech (trigger_tts_inference)
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # KW توليد_صوت,TTS,synthesis
# # FN trigger_tts_inference
# # AR Text-to-speech (trigger_tts_inference)
# # block — توليد صوت TTS
# # KW توليد_صوت,TTS,synthesis
# # block — توليد صوت TTS
# # FN trigger_tts_inference
# # AR Text-to-speech (trigger_tts_inference)
# # KW توليد_صوت,TTS,synthesis
def trigger_tts_inference(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    sample_url: Optional[str] = None,
    sample_text: str = "",
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    dialect: str = "",
    timeout: int = 180,
) -> Dict[str, Any]:
    # # block — توليد صوت TTS
    return trigger_modal_tts(
        # # block — توليد صوت TTS
        text,
        # # block — توليد صوت TTS
        lang=lang,
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        voice_id=voice_id,
        sample_url=sample_url,
        # # block — معالجة صوت/استنساخ
        sample_text=sample_text,
        dialect=dialect,
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        timeout=timeout,
    )


# # block — معالجة صوت/استنساخ
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN inference_status_summary
# # AR inference status summary (inference_status_summary)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN inference_status_summary
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR حالة المهمة (inference_status_summary)
# # KW حالة,webhook,SSE,status
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN inference_status_summary
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR حالة المهمة (inference_status_summary)
# # KW حالة,webhook,SSE,status
# # FN inference_status_summary
# # AR حالة المهمة (inference_status_summary)
# # KW حالة,webhook,SSE,status
# # FN inference_status_summary
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR حالة المهمة (inference_status_summary)
# # KW حالة,webhook,SSE,status
def inference_status_summary() -> Dict[str, Any]:
    modal_ready = bool((os.environ.get("MODAL_DUBBING_URL") or "").strip())
    # # return — إرجاع النتيجة
    return {
        "inference_provider": PROVIDER_MODAL,
        "active_inference_provider": PROVIDER_MODAL,
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        "modal_dubbing_configured": modal_ready,
        "modal_ready": modal_ready,
        "modal_tts_configured": bool((os.environ.get("MODAL_TTS_URL") or "").strip()),
        # # block — توليد صوت TTS
        "modal_dub_read_timeout_sec": _MODAL_DUB_READ_TIMEOUT,
    # # block — توليد صوت TTS
    }
