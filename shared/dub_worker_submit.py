# shared/dub_worker_submit.py — Submit dub job to RunPod or Modal
from __future__ import annotations

import logging
import os
from typing import Any, Dict

from shared import routing
from shared.dub_runpod import is_runpod_backend_url, poll_runpod_until_output
from shared.dub_webhook_url import build_modal_dub_webhook_url
from shared.inference_provider import trigger_modal_dubbing
from shared.job_events import publish_job_status
from shared.models import DubbingJob, db
from shared.supabase_quota import (
    fetch_user_quota_row,
    increment_dub_seconds_used,
    send_dub_quota_notifications,
)

logger = logging.getLogger(__name__)


def resolve_modal_dubbing_base_url() -> str:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip()
    if not modal_url:
        raise ValueError("MODAL_DUBBING_URL environment variable is not set")
    return modal_url.rstrip("/")


def _resolve_voice_sample_for_worker(voice_config: dict | None, kwargs: dict) -> tuple[str, str, str]:
    """يطابق shared/dub_modal_payload.extract_voice_sample_urls في الباكند الرئيسي."""
    vc = dict(voice_config or {})
    voice_mode = (
        kwargs.get("voice_mode")
        or vc.get("voice_mode")
        or vc.get("source")
        or "original"
    ).strip().lower()
    sample = (
        kwargs.get("sample_file")
        or kwargs.get("sample_url")
        or vc.get("sample_file")
        or vc.get("sample_url")
        or vc.get("file")
        or vc.get("url")
        or vc.get("voice_url")
        or ""
    ).strip()
    saved = (kwargs.get("saved_voice_url") or vc.get("saved_voice_url") or "").strip()
    return voice_mode, sample, saved


def build_runpod_or_modal_payload(
    job_id: str,
    media_url: str,
    lang: str,
    voice_config: dict | None,
    return_video: bool,
    kwargs: dict,
) -> Dict[str, Any]:
    vc = dict(voice_config or {})
    voice_mode, sample_file, saved_voice_url = _resolve_voice_sample_for_worker(vc, kwargs)
    if kwargs.get("use_saved_voice") and not sample_file and not saved_voice_url:
        uid = (kwargs.get("user_id") or "").strip()
        if uid:
            try:
                from shared.voice_profile import get_saved_voice

                saved = get_saved_voice(uid)
                if saved and saved.get("sample_url"):
                    saved_voice_url = saved["sample_url"].strip()
            except Exception:
                logger.exception("get_saved_voice failed for job %s", job_id)

    resolved_sample = sample_file or saved_voice_url or (vc.get("sample_url") or "").strip()
    if resolved_sample:
        vc["sample_url"] = resolved_sample
        vc["sample_file"] = resolved_sample

    sample_text = (kwargs.get("sample_text") or vc.get("sample_text") or "").strip()
    if sample_text:
        vc["sample_text"] = sample_text

    from shared.dub_engine_policy import (
        apply_high_quality_voice_defaults,
        attach_engine_fields,
        resolve_dub_force_engine,
        resolve_dub_quality,
    )

    vc = apply_high_quality_voice_defaults(
        vc,
        quality=resolve_dub_quality(body=kwargs, voice_config=vc),
    )
    forced_engine = resolve_dub_force_engine(body=kwargs, voice_config=vc)

    user_id = (kwargs.get("user_id") or "").strip()
    clone_source = (kwargs.get("clone_source") or vc.get("clone_source") or "").strip().lower()

    if not return_video:
        return_video = bool(vc.get("video_output", kwargs.get("return_video", True)))

    sample_source_url = (
        kwargs.get("sample_source_url")
        or vc.get("sample_source_url")
        or ""
    ).strip()

    payload: Dict[str, Any] = {
        "job_id": job_id,
        "backend_job_id": job_id,
        "client_job_id": job_id,
        "user_id": user_id,
        "media_url": media_url,
        "lang": lang,
        "target_language": lang,
        "target_lang": lang,
        "voice_config": vc,
        "voice_mode": voice_mode,
        "voice_source": voice_mode,
        "clone_source": clone_source or vc.get("clone_source") or "",
        "sample_url": resolved_sample,
        "sample_source_url": sample_source_url or resolved_sample,
        "sample_file": resolved_sample or sample_file,
        "saved_voice_url": saved_voice_url,
        "return_video": return_video,
        "quality": vc.get("quality") or resolve_dub_quality(body=kwargs, voice_config=vc),
    }
    payload = attach_engine_fields(payload, forced_engine)
    logger.info(
        "modal payload job=%s lang=%s clone_source=%s force_engine=%s ref_text_len=%d",
        job_id,
        lang,
        payload.get("clone_source") or "-",
        forced_engine or "auto-chain",
        len((vc.get("sample_text") or "")),
    )
    source_language = (kwargs.get("source_language") or vc.get("source_language") or "").strip()
    if source_language:
        payload["source_language"] = source_language
        vc["source_language"] = source_language
    source_dialect = (kwargs.get("source_dialect") or vc.get("source_dialect") or "").strip()
    if source_dialect:
        payload["source_dialect"] = source_dialect
        vc["source_dialect"] = source_dialect
    dialect = (vc.get("dialect") or kwargs.get("dialect") or "").strip()
    if dialect:
        payload["dialect"] = dialect
        vc["dialect"] = dialect
    if kwargs.get("translate") is False or vc.get("translate") is False:
        payload["translate"] = False
        vc["translate"] = False
    payload["voice_config"] = vc
    callback = build_modal_dub_webhook_url(job_id)
    if callback:
        payload["webhook_url"] = callback
        payload["callback_url"] = callback
    return payload


def complete_dub_job_locally(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    output: dict,
) -> None:
    final_url = output.get("output_url") or output.get("audio_url") or output.get("video_url")
    duration_seconds = int(output.get("duration_seconds", 0))
    if not final_url:
        raise RuntimeError("Backend did not return output URL")

    job.status = "completed"
    job.output_url = final_url
    db.session.commit()
    publish_job_status(job_id, {"status": "completed", "output_url": final_url})
    logger.info("Job %s completed — %ss", job_id, duration_seconds)

    if duration_seconds > 0 and user_id and user_id != "default_user":
        user_info = fetch_user_quota_row(user_id)
        updated = increment_dub_seconds_used(user_id, duration_seconds)
        if user_info and updated:
            send_dub_quota_notifications(user_info, updated)


def submit_dub_to_runpod(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    backend_url: str,
    payload: dict,
) -> None:
    output = poll_runpod_until_output(backend_url, payload)
    complete_dub_job_locally(job, job_id, user_id, output)


def submit_dub_to_modal(job_id: str, payload: dict) -> None:
    from shared.modal_job_map import extract_modal_ids_from_response, link_modal_to_backend

    modal_resp = trigger_modal_dubbing(payload)
    for ext_id in extract_modal_ids_from_response(modal_resp):
        if ext_id != job_id:
            link_modal_to_backend(ext_id, job_id)

    if isinstance(modal_resp, dict) and modal_resp.get("spawned_unconfirmed"):
        publish_job_status(
            job_id,
            {
                "status": "processing",
                "stage": "waiting",
                "message": "Modal is starting (cold start) — result will arrive via webhook",
            },
        )

    callback = payload.get("webhook_url") or ""
    logger.info(
        "Job %s submitted to Modal (resp=%s) — await webhook %s",
        job_id,
        modal_resp,
        callback or "(none)",
    )


def submit_dub_to_local(job: DubbingJob, job_id: str, user_id: str, payload: dict) -> None:
    """POST to the local GPU server (local_server.py) and await webhook — same async
    pattern as Modal so the rest of the system is unchanged."""
    import requests as _req
    local_url = (os.environ.get("LOCAL_PROCESSING_URL") or "").strip().rstrip("/")
    if not local_url:
        raise ValueError("LOCAL_PROCESSING_URL must be set when EXECUTION_MODE=local")
    resp = _req.post(f"{local_url}/upload-from-url", json=payload, timeout=60)
    resp.raise_for_status()
    publish_job_status(
        job_id,
        {"status": "processing", "stage": "waiting", "message": "Local GPU is processing — result will arrive via webhook"},
    )
    logger.info("Job %s submitted to local server at %s — awaiting webhook", job_id, local_url)


def run_dub_worker_pipeline(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    file_key: str,
    lang: str,
    voice_config: dict | None,
    return_video: bool,
    **kwargs: Any,
) -> None:
    from shared import r2_client

    media_url = r2_client.generate_download_url(file_key)
    if not media_url:
        raise RuntimeError("Failed to generate media_url from R2")

    payload = build_runpod_or_modal_payload(
        job_id, media_url, lang, voice_config, return_video, kwargs,
    )

    # ── Local mode: bypass Modal/RunPod and call the local GPU server ──────
    if config.EXECUTION_MODE == "local":
        submit_dub_to_local(job, job_id, user_id, payload)
        return

    # ── Cloud mode: existing Modal / RunPod routing ─────────────────────────
    backend_url = routing.get_dubbing_url()
    if not is_runpod_backend_url(backend_url):
        backend_url = resolve_modal_dubbing_base_url()

    if is_runpod_backend_url(backend_url):
        submit_dub_to_runpod(job, job_id, user_id, backend_url, payload)
    else:
        submit_dub_to_modal(job_id, payload)


def fail_dub_job_permanently(job: DubbingJob, job_id: str, error: Exception) -> None:
    logger.error("Job %s failed permanently: %s", job_id, error)
    job.status = "failed"
    job.error = str(error)
    db.session.commit()
    publish_job_status(job_id, {"status": "failed", "error": str(error)})
