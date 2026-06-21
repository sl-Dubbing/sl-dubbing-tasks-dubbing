# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_worker_submit.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_worker_submit.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_worker_submit.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
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


# # FN resolve_modal_dubbing_base_url
# # AR حل/استنتاج modal dubbing base url (resolve_modal_dubbing_base_url)
# # FN resolve_modal_dubbing_base_url
# # AR مهام المعالجة (resolve_modal_dubbing_base_url)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN resolve_modal_dubbing_base_url
# # AR مهام المعالجة (resolve_modal_dubbing_base_url)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def resolve_modal_dubbing_base_url() -> str:
    modal_url = (os.environ.get("MODAL_DUBBING_URL") or "").strip()
    if not modal_url:
        # # raise — رفع خطأ للم caller
        raise ValueError("MODAL_DUBBING_URL environment variable is not set")
    # # return — إرجاع النتيجة
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    return modal_url.rstrip("/")


# # FN _resolve_voice_sample_for_worker
# # AR حل/استنتاج voice sample for worker (_resolve_voice_sample_for_worker)
# # FN _resolve_voice_sample_for_worker
# # AR الصوت والاستنساخ (_resolve_voice_sample_for_worker)
# # block — معالجة صوت/استنساخ
# # KW صوت,استنساخ,voice,clone,sample,مهمة,job,polling,celery,worker
# # FN _resolve_voice_sample_for_worker
# # AR الصوت والاستنساخ (_resolve_voice_sample_for_worker)
# # KW صوت,استنساخ,voice,clone,sample,مهمة,job,polling,celery,worker
def _resolve_voice_sample_for_worker(voice_config: dict | None, kwargs: dict) -> tuple[str, str, str]:
    """يطابق shared/dub_modal_payload.extract_voice_sample_urls في الباكند الرئيسي."""
    vc = dict(voice_config or {})
    voice_mode = (
        kwargs.get("voice_mode")
        or vc.get("voice_mode")
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        or vc.get("source")
        or "original"
    ).strip().lower()
    sample = (
        kwargs.get("sample_file")
        # # block — معالجة صوت/استنساخ
        or kwargs.get("sample_url")
        # # block — معالجة صوت/استنساخ
        or vc.get("sample_file")
        or vc.get("sample_url")
        or vc.get("file")
        or vc.get("url")
        # # block — معالجة صوت/استنساخ
        or vc.get("voice_url")
        or ""
    # # block — معالجة صوت/استنساخ
    ).strip()
    saved = (kwargs.get("saved_voice_url") or vc.get("saved_voice_url") or "").strip()
    # # return — إرجاع النتيجة
    # # block — معالجة صوت/استنساخ
    return voice_mode, sample, saved


# # FN build_runpod_or_modal_payload
# # AR بناء runpod or modal payload (build_runpod_or_modal_payload)
# # block — معالجة صوت/استنساخ
# # FN build_runpod_or_modal_payload
# # AR مهام المعالجة (build_runpod_or_modal_payload)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN build_runpod_or_modal_payload
# # AR مهام المعالجة (build_runpod_or_modal_payload)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def build_runpod_or_modal_payload(
    job_id: str,
    media_url: str,
    lang: str,
    voice_config: dict | None,
    return_video: bool,
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    kwargs: dict,
) -> Dict[str, Any]:
    vc = dict(voice_config or {})
    voice_mode, sample_file, saved_voice_url = _resolve_voice_sample_for_worker(vc, kwargs)
    if kwargs.get("use_saved_voice") and not sample_file and not saved_voice_url:
        # # block — معالجة صوت/استنساخ
        uid = (kwargs.get("user_id") or "").strip()
        # # block — معالجة صوت/استنساخ
        if uid:
            # # try — عملية قد تفشل
            # # try — عملية قد تفشل
            try:
                # # block — معالجة صوت/استنساخ
                from shared.voice_profile import get_saved_voice

                saved = get_saved_voice(uid)
                if saved and saved.get("sample_url"):
                    # # block — معالجة صوت/استنساخ
                    saved_voice_url = saved["sample_url"].strip()
            # # catch — التقاط خطأ
            # # block — معالجة صوت/استنساخ
            # # catch — التقاط خطأ
            except Exception:
                logger.exception("get_saved_voice failed for job %s", job_id)

    resolved_sample = sample_file or saved_voice_url or (vc.get("sample_url") or "").strip()
    if resolved_sample:
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        vc["sample_url"] = resolved_sample
        vc["sample_file"] = resolved_sample

    sample_text = (kwargs.get("sample_text") or vc.get("sample_text") or "").strip()
    if sample_text:
        vc["sample_text"] = sample_text

    from shared.dub_engine_policy import (
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        apply_high_quality_voice_defaults,
        attach_engine_fields,
        resolve_dub_force_engine,
        resolve_dub_quality,
    )

    # # block — معالجة صوت/استنساخ
    vc = apply_high_quality_voice_defaults(
        # # block — معالجة صوت/استنساخ
        vc,
        quality=resolve_dub_quality(body=kwargs, voice_config=vc),
    )
    forced_engine = resolve_dub_force_engine(body=kwargs, voice_config=vc)

    # # block — معالجة صوت/استنساخ
    user_id = (kwargs.get("user_id") or "").strip()
    clone_source = (kwargs.get("clone_source") or vc.get("clone_source") or "").strip().lower()

    # # block — معالجة صوت/استنساخ
    if not return_video:
        return_video = bool(vc.get("video_output", kwargs.get("return_video", True)))

    sample_source_url = (
        # # block — معالجة صوت/استنساخ
        kwargs.get("sample_source_url")
        or vc.get("sample_source_url")
        or ""
    # # block — معالجة صوت/استنساخ
    ).strip()

    payload: Dict[str, Any] = {
        # # block — معالجة صوت/استنساخ
        "job_id": job_id,
        "backend_job_id": job_id,
        "client_job_id": job_id,
        "user_id": user_id,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        "media_url": media_url,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        "lang": lang,
        "target_language": lang,
        "target_lang": lang,
        "voice_config": vc,
        "voice_mode": voice_mode,
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        "voice_source": voice_mode,
        "clone_source": clone_source or vc.get("clone_source") or "",
        "sample_url": resolved_sample,
        "sample_source_url": sample_source_url or resolved_sample,
        "sample_file": resolved_sample or sample_file,
        "saved_voice_url": saved_voice_url,
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        "return_video": return_video,
        "quality": vc.get("quality") or resolve_dub_quality(body=kwargs, voice_config=vc),
    }
    payload = attach_engine_fields(payload, forced_engine)
    logger.info(
        # # block — معالجة صوت/استنساخ
        "modal payload job=%s lang=%s clone_source=%s force_engine=%s ref_text_len=%d",
        # # block — معالجة صوت/استنساخ
        job_id,
        lang,
        payload.get("clone_source") or "-",
        forced_engine or "auto-chain",
        # # block — معالجة صوت/استنساخ
        len((vc.get("sample_text") or "")),
    )
    # # block — معالجة صوت/استنساخ
    source_language = (kwargs.get("source_language") or vc.get("source_language") or "").strip()
    if source_language:
        payload["source_language"] = source_language
        # # block — تنفيذ منطق — راجع الأسطر التالية
        vc["source_language"] = source_language
    source_dialect = (kwargs.get("source_dialect") or vc.get("source_dialect") or "").strip()
    if source_dialect:
        # # block — تنفيذ منطق — راجع الأسطر التالية
        payload["source_dialect"] = source_dialect
        vc["source_dialect"] = source_dialect
    # # block — تنفيذ منطق — راجع الأسطر التالية
    dialect = (vc.get("dialect") or kwargs.get("dialect") or "").strip()
    if dialect:
        payload["dialect"] = dialect
        vc["dialect"] = dialect
    # # block — خطوة ترجمة (مترجم)
    if kwargs.get("translate") is False or vc.get("translate") is False:
        # # block — خطوة ترجمة (مترجم)
        payload["translate"] = False
        vc["translate"] = False
    payload["voice_config"] = vc
    callback = build_modal_dub_webhook_url(job_id)
    if callback:
        # # block — خطوة ترجمة (مترجم)
        # # block — خطوة ترجمة (مترجم)
        payload["webhook_url"] = callback
        payload["callback_url"] = callback
    return payload


# # FN complete_dub_job_locally
# # AR complete dub job locally (complete_dub_job_locally)
# # FN complete_dub_job_locally
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR مهام المعالجة (complete_dub_job_locally)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN complete_dub_job_locally
# # AR مهام المعالجة (complete_dub_job_locally)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def complete_dub_job_locally(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    output: dict,
) -> None:
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    final_url = output.get("output_url") or output.get("audio_url") or output.get("video_url")
    duration_seconds = int(output.get("duration_seconds", 0))
    if not final_url:
        raise RuntimeError("Backend did not return output URL")

    job.status = "completed"
    # # block — معالجة أخطاء
    job.output_url = final_url
    # # block — معالجة أخطاء
    db.session.commit()
    publish_job_status(job_id, {"status": "completed", "output_url": final_url})
    logger.info("Job %s completed — %ss", job_id, duration_seconds)

    if duration_seconds > 0 and user_id and user_id != "default_user":
        # # block — قاعدة بيانات
        user_info = fetch_user_quota_row(user_id)
        updated = increment_dub_seconds_used(user_id, duration_seconds)
        # # block — تنفيذ منطق — راجع الأسطر التالية
        if user_info and updated:
            send_dub_quota_notifications(user_info, updated)


# # FN submit_dub_to_runpod
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR submit dub to runpod (submit_dub_to_runpod)
# # FN submit_dub_to_runpod
# # AR مهام المعالجة (submit_dub_to_runpod)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker
# # FN submit_dub_to_runpod
# # block — enqueue Celery
# # AR مهام المعالجة (submit_dub_to_runpod)
# # KW مهمة,job,polling,celery,worker
def submit_dub_to_runpod(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    backend_url: str,
    payload: dict,
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
) -> None:
    output = poll_runpod_until_output(backend_url, payload)
    complete_dub_job_locally(job, job_id, user_id, output)


# # FN submit_dub_to_modal
# # AR submit dub to modal (submit_dub_to_modal)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN submit_dub_to_modal
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR مهام المعالجة (submit_dub_to_modal)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN submit_dub_to_modal
# # AR مهام المعالجة (submit_dub_to_modal)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def submit_dub_to_modal(job_id: str, payload: dict) -> None:
    from shared.modal_job_map import extract_modal_ids_from_response, link_modal_to_backend

    modal_resp = trigger_modal_dubbing(payload)
    for ext_id in extract_modal_ids_from_response(modal_resp):
        if ext_id != job_id:
            link_modal_to_backend(ext_id, job_id)

    # # block — حلقة/تكرار
    # # block — حلقة/تكرار
    if isinstance(modal_resp, dict) and modal_resp.get("spawned_unconfirmed"):
        publish_job_status(
            job_id,
            {
                "status": "processing",
                # # block — تنفيذ منطق — راجع الأسطر التالية
                "stage": "waiting",
                # # block — تنفيذ منطق — راجع الأسطر التالية
                "message": "Modal is starting (cold start) — result will arrive via webhook",
            },
        )

    callback = payload.get("webhook_url") or ""
    # # block — تنفيذ منطق — راجع الأسطر التالية
    logger.info(
        "Job %s submitted to Modal (resp=%s) — await webhook %s",
        # # block — تنفيذ منطق — راجع الأسطر التالية
        job_id,
        modal_resp,
        callback or "(none)",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    )


# # FN submit_dub_to_local
# # AR submit dub to local (submit_dub_to_local)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN submit_dub_to_local
# # AR مهام المعالجة (submit_dub_to_local)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
# # FN submit_dub_to_local
# # AR مهام المعالجة (submit_dub_to_local)
# # KW مهمة,job,polling,celery,worker,تنفيذ,local,cloud,modal,parity
def submit_dub_to_local(job: DubbingJob, job_id: str, user_id: str, payload: dict) -> None:
    """POST to the local GPU server (local_server.py) and await webhook — same async
    pattern as Modal so the rest of the system is unchanged."""
    import requests as _req
    local_url = (os.environ.get("LOCAL_PROCESSING_URL") or "").strip().rstrip("/")
    if not local_url:
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — معالجة أخطاء
        # # raise — رفع خطأ للم caller
        raise ValueError("LOCAL_PROCESSING_URL must be set when EXECUTION_MODE=local")
    from shared.security import inference_request_headers

    resp = _req.post(
        f"{local_url}/upload-from-url",
        # # block — رفع أو تخزين ملف
        json=payload,
        # # block — رفع أو تخزين ملف
        headers=inference_request_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    # # block — معالجة أخطاء
    publish_job_status(
        job_id,
        # # block — معالجة أخطاء
        {"status": "processing", "stage": "waiting", "message": "Local GPU is processing — result will arrive via webhook"},
    )
    logger.info("Job %s submitted to local server at %s — awaiting webhook", job_id, local_url)


# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN run_dub_worker_pipeline
# # AR تشغيل dub worker pipeline (run_dub_worker_pipeline)
# # FN run_dub_worker_pipeline
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR مهام المعالجة (run_dub_worker_pipeline)
# # KW مهمة,job,polling,celery,worker
# # block — enqueue Celery
# # FN run_dub_worker_pipeline
# # AR مهام المعالجة (run_dub_worker_pipeline)
# # KW مهمة,job,polling,celery,worker
def run_dub_worker_pipeline(
    job: DubbingJob,
    job_id: str,
    user_id: str,
    file_key: str,
    lang: str,
    # # block — رفع أو تخزين ملف
    # # block — معالجة صوت/استنساخ
    voice_config: dict | None,
    return_video: bool,
    **kwargs: Any,
) -> None:
    from shared import r2_client

    # # block — معالجة صوت/استنساخ
    media_url = r2_client.generate_download_url(file_key)
    # # block — رفع أو تخزين ملف
    if not media_url:
        raise RuntimeError("Failed to generate media_url from R2")

    payload = build_runpod_or_modal_payload(
        job_id, media_url, lang, voice_config, return_video, kwargs,
    # # block — معالجة صوت/استنساخ
    )

    # ── Local mode: bypass Modal/RunPod and call the local GPU server ──────
    # # guard — رفض/خروج
    # # block — معالجة صوت/استنساخ
    # # guard — رفض/خروج
    if (os.environ.get("EXECUTION_MODE") or "cloud").strip().lower() == "local":
        submit_dub_to_local(job, job_id, user_id, payload)
        # # block — فرع شرطي
        return

    # ── Cloud mode: existing Modal / RunPod routing ─────────────────────────
    backend_url = routing.get_dubbing_url()
    if not is_runpod_backend_url(backend_url):
        backend_url = resolve_modal_dubbing_base_url()

    # # block — إرجاع نتيجة
    if is_runpod_backend_url(backend_url):
        # # block — تنفيذ منطق — راجع الأسطر التالية
        submit_dub_to_runpod(job, job_id, user_id, backend_url, payload)
    else:
        submit_dub_to_modal(job_id, payload)


# # FN fail_dub_job_permanently
# # AR fail dub job permanently (fail_dub_job_permanently)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN fail_dub_job_permanently
# # AR مهام المعالجة (fail_dub_job_permanently)
# # KW مهمة,job,polling,celery,worker
# # FN fail_dub_job_permanently
# # AR مهام المعالجة (fail_dub_job_permanently)
# # KW مهمة,job,polling,celery,worker
def fail_dub_job_permanently(job: DubbingJob, job_id: str, error: Exception) -> None:
    logger.error("Job %s failed permanently: %s", job_id, error)
    job.status = "failed"
    job.error = str(error)
    db.session.commit()
    publish_job_status(job_id, {"status": "failed", "error": str(error)})
