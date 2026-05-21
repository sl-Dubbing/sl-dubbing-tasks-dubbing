# shared/inference_provider.py — Modal vs Fal.ai inference routing
"""
Switch providers with INFERENCE_PROVIDER=modal|fal (default: modal).

Secrets:
  modal — MODAL_DUBBING_URL, MODAL_TOKEN_SECRET (optional)
  fal   — FAL_KEY, FAL_DUBBING_ENDPOINT, optional FAL_TTS_ENDPOINT
          pip: fal-client (reads FAL_KEY from the environment)
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

PROVIDER_MODAL = "modal"
PROVIDER_FAL = "fal"
_VALID_PROVIDERS = frozenset({PROVIDER_MODAL, PROVIDER_FAL})


class InferenceProviderError(Exception):
    """Misconfiguration or upstream inference failure."""


def get_inference_provider() -> str:
    """INFERENCE_PROVIDER env (default 'modal')."""
    return (os.environ.get("INFERENCE_PROVIDER") or "modal").strip().lower()


def get_active_inference_provider() -> str:
    """
    Primary: INFERENCE_PROVIDER (default modal).
    Optional override: ACTIVE_INFERENCE_PROVIDER.
    """
    raw = (
        os.environ.get("ACTIVE_INFERENCE_PROVIDER")
        or get_inference_provider()
        or PROVIDER_MODAL
    ).strip().lower()
    if raw in _VALID_PROVIDERS:
        return raw
    legacy = (os.environ.get("PROCESSING_BACKEND") or "modal").strip().lower()
    if legacy == PROVIDER_FAL:
        return PROVIDER_FAL
    return PROVIDER_MODAL


def get_fal_key() -> str:
    """Load Fal API key from environment (never log the value)."""
    key = (
        os.environ.get("FAL_KEY")
        or os.environ.get("FAL_API_KEY")
        or ""
    ).strip()
    if not key:
        raise InferenceProviderError(
            "FAL_KEY (or FAL_API_KEY) is required when INFERENCE_PROVIDER=fal"
        )
    return key


def _ensure_fal_key_in_env() -> None:
    """fal-client authenticates via FAL_KEY; set from env without logging."""
    key = get_fal_key()
    if not os.environ.get("FAL_KEY"):
        os.environ["FAL_KEY"] = key


def _import_fal_client():
    """Secure import: requires FAL_KEY and fal-client package."""
    _ensure_fal_key_in_env()
    try:
        import fal_client  # noqa: PLC0415 — lazy import when provider=fal only
    except ImportError as exc:
        raise InferenceProviderError(
            "fal-client is not installed. Add fal-client to requirements.txt and pip install."
        ) from exc
    return fal_client


def _resolve_fal_model_id(endpoint: str) -> str:
    ep = (endpoint or "").strip().rstrip("/")
    if not ep:
        raise InferenceProviderError(
            "FAL_DUBBING_ENDPOINT is required when INFERENCE_PROVIDER=fal "
            "(e.g. fal-ai/your-workflow)"
        )
    if ep.startswith("http://") or ep.startswith("https://"):
        if "queue.fal.run/" in ep:
            return ep.split("queue.fal.run/", 1)[-1].strip("/")
        raise InferenceProviderError(
            "FAL_DUBBING_ENDPOINT URL must be a queue.fal.run model URL"
        )
    return ep.lstrip("/")


def _fal_auth_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Key {get_fal_key()}",
        "Content-Type": "application/json",
    }


def _normalize_fal_queue_url(endpoint: str) -> str:
    ep = (endpoint or "").strip().rstrip("/")
    if not ep:
        raise InferenceProviderError(
            "FAL_DUBBING_ENDPOINT is required when ACTIVE_INFERENCE_PROVIDER=fal "
            "(e.g. fal-ai/your-workflow or https://queue.fal.run/fal-ai/your-workflow)"
        )
    if ep.startswith("http://") or ep.startswith("https://"):
        return ep
    if ep.startswith("fal-ai/") or ep.startswith("fal/"):
        return f"https://queue.fal.run/{ep}"
    return f"https://queue.fal.run/fal-ai/{ep}"


def _build_fal_dubbing_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Map Celery/Modal payload fields to a generic Fal workflow input dict."""
    voice_cfg = payload.get("voice_config") or {}
    if isinstance(voice_cfg, dict):
        voice_source = voice_cfg.get("source") or payload.get("voice_source") or "original"
        sample_file = voice_cfg.get("sample_file") or payload.get("sample_file")
    else:
        voice_source = payload.get("voice_source") or "original"
        sample_file = payload.get("sample_file")

    fal_input: Dict[str, Any] = {
        "media_url": payload.get("media_url"),
        "lang": payload.get("lang") or payload.get("target_language"),
        "target_language": payload.get("lang") or payload.get("target_language"),
        "job_id": payload.get("job_id") or payload.get("backend_job_id"),
        "voice_mode": voice_source,
        "voice_source": voice_source,
        "return_video": payload.get("return_video", True),
        "engine": payload.get("engine"),
    }
    if payload.get("source_language"):
        fal_input["source_language"] = payload["source_language"]
    if sample_file:
        fal_input["sample_file"] = sample_file
    webhook = payload.get("webhook_url") or payload.get("callback_url")
    if webhook:
        fal_input["webhook_url"] = webhook
    return {k: v for k, v in fal_input.items() if v is not None}


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


def trigger_fal_dubbing(payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Submit dubbing to Fal via fal_client (FAL_KEY from environment).
    Default: fal_client.submit (async + optional webhook).
    Set FAL_DUBBING_USE_SUBSCRIBE=1 to block with fal_client.subscribe instead.
    """
    fal = _import_fal_client()
    model_id = _resolve_fal_model_id(os.environ.get("FAL_DUBBING_ENDPOINT", ""))
    fal_input = _build_fal_dubbing_input(payload)
    webhook = payload.get("webhook_url") or payload.get("callback_url")
    job_id = payload.get("job_id") or payload.get("backend_job_id")

    use_subscribe = os.environ.get("FAL_DUBBING_USE_SUBSCRIBE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    if use_subscribe:
        logger.info(
            "Fal dub subscribe (blocking): %s (job_id=%s)",
            model_id,
            job_id,
        )
        subscribe_kwargs: Dict[str, Any] = {"arguments": fal_input}
        if webhook:
            subscribe_kwargs["webhook_url"] = webhook
        result = fal.subscribe(model_id, **subscribe_kwargs)
        return {
            "success": True,
            "provider": PROVIDER_FAL,
            "job_id": job_id,
            "status": "completed",
            "result": result,
        }

    submit_kwargs: Dict[str, Any] = {"arguments": fal_input}
    if webhook:
        submit_kwargs["webhook_url"] = webhook

    logger.info("Fal dub submit (async): %s (job_id=%s)", model_id, job_id)
    handler = fal.submit(model_id, **submit_kwargs)
    request_id = getattr(handler, "request_id", None) or str(handler)
    return {
        "success": True,
        "provider": PROVIDER_FAL,
        "job_id": job_id,
        "request_id": request_id,
        "status": "queued",
    }


def trigger_dubbing_job(payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """Dispatch dubbing to INFERENCE_PROVIDER (modal | fal)."""
    provider = get_active_inference_provider()
    if provider == PROVIDER_MODAL:
        return trigger_modal_dubbing(payload, timeout=timeout)
    if provider == PROVIDER_FAL:
        return trigger_fal_dubbing(payload, timeout=timeout)
    raise InferenceProviderError(f"Unsupported INFERENCE_PROVIDER: {provider!r}")


def _normalize_fal_tts_url(endpoint: str) -> str:
    ep = (endpoint or "").strip().rstrip("/")
    if not ep:
        raise InferenceProviderError(
            "FAL_TTS_ENDPOINT is required for Fal TTS (e.g. fal-ai/elevenlabs/tts/multilingual-v2)"
        )
    if ep.startswith("http"):
        return ep
    if ep.startswith("fal-ai/") or ep.startswith("fal/"):
        return f"https://queue.fal.run/{ep}"
    return f"https://queue.fal.run/fal-ai/{ep}"


def trigger_fal_tts(
    text: str,
    lang: str = "en",
    voice_id: Optional[str] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Run TTS via fal_client.subscribe (default) or submit + get."""
    _ = timeout  # reserved for future timeout wiring in subscribe
    endpoint = os.environ.get("FAL_TTS_ENDPOINT", "").strip()
    if not endpoint:
        raise InferenceProviderError(
            "FAL_TTS_ENDPOINT is required for Fal TTS (e.g. fal-ai/elevenlabs/tts/multilingual-v2)"
        )
    fal_input: Dict[str, Any] = {"text": text, "language": lang}
    if voice_id:
        fal_input["voice"] = voice_id

    fal = _import_fal_client()
    model_id = _resolve_fal_model_id(endpoint)

    use_subscribe = os.environ.get("FAL_TTS_USE_SUBSCRIBE", "1").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if use_subscribe:
        result = fal.subscribe(model_id, arguments=fal_input)
    else:
        handler = fal.submit(model_id, arguments=fal_input)
        result = handler.get() if hasattr(handler, "get") else handler

    if isinstance(result, dict):
        audio_url = (
            result.get("audio_url")
            or result.get("url")
            or (result.get("audio") or {}).get("url")
        )
        return {"ok": True, "provider": PROVIDER_FAL, "audio_url": audio_url, "raw": result}
    return {"ok": False, "error": "Unexpected Fal TTS response shape", "raw": result}


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
    """Dispatch TTS to active provider (modal | fal)."""
    provider = get_active_inference_provider()
    if provider == PROVIDER_FAL:
        return trigger_fal_tts(text, lang=lang, voice_id=voice_id, timeout=timeout)
    if provider == PROVIDER_MODAL:
        return trigger_modal_tts(text, lang=lang, voice_id=voice_id, timeout=timeout)
    raise InferenceProviderError(f"Unsupported INFERENCE_PROVIDER: {provider!r}")


def inference_status_summary() -> Dict[str, Any]:
    """Safe status blob for /health and /api/status (no secrets)."""
    from shared.fal_dubbing_pipeline import is_fal_pipeline_configured

    provider = get_active_inference_provider()
    fal_ready = is_fal_pipeline_configured()
    summary: Dict[str, Any] = {
        "inference_provider": provider,
        "active_inference_provider": provider,
        "modal_dubbing_configured": bool((os.environ.get("MODAL_DUBBING_URL") or "").strip()),
        "fal_key_configured": bool(
            (os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY") or "").strip()
        ),
        # Dual-engine Fal pipeline uses per-stage models (Whisper + TTS), not only FAL_DUBBING_ENDPOINT
        "fal_dubbing_endpoint_configured": fal_ready,
        "fal_ready": fal_ready,
        "fal_whisper_model": os.environ.get("FAL_WHISPER_MODEL") or "fal-ai/whisper",
        "fal_tts_model": (
            os.environ.get("FAL_TTS_MODEL")
            or os.environ.get("FAL_TTS_ENDPOINT")
            or "fal-ai/elevenlabs/tts/multilingual-v2"
        ),
    }
    if provider == PROVIDER_MODAL:
        summary["modal_ready"] = summary["modal_dubbing_configured"]
    return summary
