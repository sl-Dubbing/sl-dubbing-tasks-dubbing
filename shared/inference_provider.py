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


def get_inference_provider() -> str:
    return PROVIDER_MODAL


def get_active_inference_provider() -> str:
    return PROVIDER_MODAL


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


_MODAL_DUB_CONNECT_TIMEOUT = _int_env("MODAL_DUB_CONNECT_TIMEOUT", 10)
_MODAL_DUB_READ_TIMEOUT = _int_env("MODAL_DUB_READ_TIMEOUT", 120)
_MODAL_PAYLOAD_VERSION = "v2-normalize"


def _normalize_modal_dub_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(payload or {})
    raw_vc = p.get("voice_config") or p.get("voice") or {}
    vc = dict(raw_vc) if isinstance(raw_vc, dict) else {}

    top_sample = (
        p.get("sample_url") or p.get("sample_file") or p.get("voice_url") or p.get("url") or ""
    ).strip()
    inner_sample = (
        vc.get("sample_url") or vc.get("sample_file") or vc.get("url") or vc.get("voice_url") or ""
    ).strip()
    sample = top_sample or inner_sample

    if sample:
        p["sample_url"] = sample
        p["sample_file"] = sample
        if not (vc.get("sample_url") or vc.get("sample_file") or "").strip():
            vc["sample_url"] = sample
            vc["sample_file"] = sample

    sample_text = (p.get("sample_text") or vc.get("sample_text") or "").strip()
    if sample_text:
        vc["sample_text"] = sample_text

    p["voice_config"] = vc
    return p


def trigger_modal_dubbing(payload: Dict[str, Any], timeout=None) -> Dict[str, Any]:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip().rstrip("/")
    if not modal_url:
        raise InferenceProviderError("MODAL_DUBBING_URL environment variable is not set")
    if timeout is None:
        timeout = (_MODAL_DUB_CONNECT_TIMEOUT, _MODAL_DUB_READ_TIMEOUT)
    upload_url = f"{modal_url}/upload-from-url"
    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    payload = _normalize_modal_dub_payload(payload)
    vc = payload.get("voice_config") if isinstance(payload.get("voice_config"), dict) else {}
    logger.info(
        "Payload to Modal (%s): job_id=%s lang=%s sample_url=%r voice_config.sample_url=%r keys=%s",
        _MODAL_PAYLOAD_VERSION,
        payload.get("job_id"),
        payload.get("lang"),
        (payload.get("sample_url") or "").strip(),
        (vc.get("sample_url") or "").strip(),
        sorted(payload.keys()),
    )

    last_exc = None
    for attempt in range(1, 4):
        try:
            r = requests.post(upload_url, json=payload, headers=headers, timeout=timeout)
            if r.status_code >= 500:
                logger.warning("Modal returned %s (attempt %s/3), retrying...", r.status_code, attempt)
                last_exc = InferenceProviderError(f"Modal {r.status_code}")
                time.sleep(3 * attempt)
                continue
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                data.setdefault("provider", PROVIDER_MODAL)
            return data

        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            logger.warning(
                "Modal cold-start/timeout (attempt %s/3): %s — retrying...",
                attempt,
                exc,
            )
            time.sleep(5 * attempt)

        except requests.exceptions.RequestException as exc:
            last_exc = exc
            logger.warning("Modal request failed (attempt %s/3): %s", attempt, exc)
            time.sleep(3 * attempt)

    logger.warning(
        "Modal did not confirm within retries (job_id=%s): %s — "
        "assuming spawned; webhook is source of truth",
        payload.get("job_id"),
        last_exc,
    )
    return {
        "success": True,
        "status": "processing",
        "spawned_unconfirmed": True,
        "job_id": payload.get("job_id"),
        "provider": PROVIDER_MODAL,
        "warning": f"Modal did not confirm in time: {last_exc}",
    }


def trigger_dubbing_job(payload: Dict[str, Any], timeout=None) -> Dict[str, Any]:
    return trigger_modal_dubbing(payload, timeout=timeout)


def trigger_modal_cancel(job_id: str, timeout: int = 10) -> Dict[str, Any]:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip().rstrip("/")
    if not modal_url:
        raise InferenceProviderError("MODAL_DUBBING_URL environment variable is not set")

    cancel_url = f"{modal_url}/cancel"
    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    payload = {"job_id": (job_id or "").strip()}
    r = requests.post(cancel_url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, dict) else {"success": True}


def trigger_modal_tts(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    sample_url: Optional[str] = None,
    sample_text: str = "",
    dialect: str = "",
    timeout: int = 180,
) -> Dict[str, Any]:
    modal_tts_url = (os.environ.get("MODAL_TTS_URL") or "").strip().rstrip("/")
    if not modal_tts_url:
        raise InferenceProviderError("MODAL_TTS_URL is not set for Modal TTS inference")

    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    body: Dict[str, Any] = {
        "text": text,
        "lang": lang,
        "lang_code": lang,
        "voice_id": voice_id,
        "sample_url": sample_url,
    }
    if sample_text:
        body["sample_text"] = sample_text
    if dialect:
        body["dialect"] = dialect
    r = requests.post(f"{modal_tts_url}/synthesize", json=body, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        data.setdefault("provider", PROVIDER_MODAL)
    return data


def trigger_tts_inference(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    sample_url: Optional[str] = None,
    sample_text: str = "",
    dialect: str = "",
    timeout: int = 180,
) -> Dict[str, Any]:
    return trigger_modal_tts(
        text,
        lang=lang,
        voice_id=voice_id,
        sample_url=sample_url,
        sample_text=sample_text,
        dialect=dialect,
        timeout=timeout,
    )


def inference_status_summary() -> Dict[str, Any]:
    modal_ready = bool((os.environ.get("MODAL_DUBBING_URL") or "").strip())
    return {
        "inference_provider": PROVIDER_MODAL,
        "active_inference_provider": PROVIDER_MODAL,
        "modal_dubbing_configured": modal_ready,
        "modal_ready": modal_ready,
        "modal_tts_configured": bool((os.environ.get("MODAL_TTS_URL") or "").strip()),
        "modal_dub_read_timeout_sec": _MODAL_DUB_READ_TIMEOUT,
    }
