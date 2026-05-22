# shared/inference_provider.py — Modal inference routing
"""
Dubbing and quick TTS use Modal (MODAL_DUBBING_URL, optional MODAL_TTS_URL).
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

PROVIDER_MODAL = "modal"


class InferenceProviderError(Exception):
    """Misconfiguration or upstream inference failure."""


def get_inference_provider() -> str:
    """Always Modal."""
    return PROVIDER_MODAL


def get_active_inference_provider() -> str:
    return PROVIDER_MODAL


def trigger_modal_dubbing(payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip().rstrip("/")
    if not modal_url:
        raise InferenceProviderError("MODAL_DUBBING_URL environment variable is not set")

    upload_url = f"{modal_url}/upload-from-url"
    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    logger.info(
        "Triggering Modal dub job: %s (job_id=%s)",
        upload_url,
        payload.get("job_id"),
    )
    r = requests.post(upload_url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        data.setdefault("provider", PROVIDER_MODAL)
    return data


def trigger_dubbing_job(payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    return trigger_modal_dubbing(payload, timeout=timeout)


def trigger_modal_tts(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Optional Modal TTS router hook (requires MODAL_TTS_URL)."""
    modal_tts_url = (os.environ.get("MODAL_TTS_URL") or "").strip().rstrip("/")
    if not modal_tts_url:
        raise InferenceProviderError("MODAL_TTS_URL is not set for Modal TTS inference")

    headers = {"Content-Type": "application/json"}
    secret = (os.environ.get("MODAL_TOKEN_SECRET") or "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    body = {"text": text, "lang": lang, "voice_id": voice_id}
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
    timeout: int = 120,
) -> Dict[str, Any]:
    return trigger_modal_tts(text, lang=lang, voice_id=voice_id, timeout=timeout)


def inference_status_summary() -> Dict[str, Any]:
    """Safe status blob for /health and /api/status (no secrets)."""
    modal_ready = bool((os.environ.get("MODAL_DUBBING_URL") or "").strip())
    return {
        "inference_provider": PROVIDER_MODAL,
        "active_inference_provider": PROVIDER_MODAL,
        "modal_dubbing_configured": modal_ready,
        "modal_ready": modal_ready,
        "modal_tts_configured": bool((os.environ.get("MODAL_TTS_URL") or "").strip()),
    }
