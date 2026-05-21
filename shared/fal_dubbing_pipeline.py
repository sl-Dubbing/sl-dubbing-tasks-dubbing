# shared/fal_dubbing_pipeline.py — Dual-engine Fal dubbing (STT → translate → TTS → R2)
"""
Runs entirely in the Celery worker when INFERENCE_PROVIDER=fal.
Publishes Redis job events for SSE (progress 50–100) and updates dubbing_jobs like Modal webhook.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from typing import Any, Dict, Optional

import requests

from shared.inference_provider import InferenceProviderError, _import_fal_client
from shared.job_events import publish_job_status
from shared.models import DubbingJob, db

logger = logging.getLogger(__name__)

# Fal model IDs (override via env)
DEFAULT_FAL_WHISPER_MODEL = "fal-ai/whisper"
DEFAULT_FAL_TTS_MODEL = "fal-ai/elevenlabs/tts/multilingual-v2"

FAL_PROGRESS_START = 50.0
FAL_PROGRESS_END = 100.0


def is_fal_pipeline_configured() -> bool:
    """True when FAL_KEY is set and fal-client is available."""
    key = (os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY") or "").strip()
    if not key:
        return False
    try:
        _import_fal_client()
        return True
    except InferenceProviderError:
        return False


def _fal_whisper_model() -> str:
    return (os.environ.get("FAL_WHISPER_MODEL") or DEFAULT_FAL_WHISPER_MODEL).strip()


def _fal_tts_model() -> str:
    return (
        os.environ.get("FAL_TTS_MODEL")
        or os.environ.get("FAL_TTS_ENDPOINT")
        or DEFAULT_FAL_TTS_MODEL
    ).strip()


def _map_progress(stage_pct: float) -> float:
    """Map internal 0–1 stage progress to frontend band 50–100."""
    return FAL_PROGRESS_START + (FAL_PROGRESS_END - FAL_PROGRESS_START) * max(
        0.0, min(1.0, stage_pct)
    )


def _publish_progress(
    job_id: str,
    stage: str,
    stage_pct: float,
    message: Optional[str] = None,
    **extra: Any,
) -> None:
    pct = _map_progress(stage_pct)
    payload: Dict[str, Any] = {
        "status": "processing",
        "stage": stage,
        "progress": round(pct, 1),
        "provider": "fal",
    }
    if message:
        payload["message"] = message
    payload.update(extra)
    publish_job_status(job_id, payload)
    logger.info("[%s] Fal %s (%.0f%%)", job_id, stage, pct)


def _fail_job(job: DubbingJob, job_id: str, error: str) -> None:
    job.status = "failed"
    job.error = (error or "Fal dubbing failed")[:2000]
    db.session.commit()
    publish_job_status(
        job_id,
        {"status": "failed", "error": job.error, "progress": FAL_PROGRESS_START, "provider": "fal"},
    )


def _complete_job(
    job: DubbingJob,
    job_id: str,
    output_url: str,
    duration_seconds: int = 0,
    user_id: Optional[str] = None,
) -> None:
    job.status = "completed"
    job.output_url = output_url
    job.error = None
    db.session.commit()
    publish_job_status(
        job_id,
        {
            "status": "completed",
            "output_url": output_url,
            "progress": FAL_PROGRESS_END,
            "provider": "fal",
        },
    )
    if duration_seconds > 0 and user_id and user_id != "default_user":
        _apply_quota(user_id, duration_seconds)


def _apply_quota(user_id: str, duration_seconds: int) -> None:
    try:
        import importlib

        mod = importlib.import_module("tasks_dubbing")
        user_info = mod.get_user_info(user_id)
        updated = mod.update_dub_usage(user_id, duration_seconds)
        if user_info and updated:
            mod.notify_quota_if_needed(user_info, updated)
    except Exception as exc:
        logger.warning("Fal quota update skipped: %s", exc)


def _download_media(url: str, dest_path: str, timeout: int = 300) -> None:
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)


def _extract_audio_wav(video_path: str, wav_path: str) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-vn",
                "-ar",
                "16000",
                "-ac",
                "1",
                wav_path,
            ],
            check=True,
            capture_output=True,
        )
        return os.path.isfile(wav_path) and os.path.getsize(wav_path) > 0
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning("ffmpeg extract failed: %s", exc)
        return False


def _upload_temp_to_r2(local_path: str, job_id: str, ext: str, content_type: str) -> Optional[str]:
    from shared import r2_client

    try:
        s3 = r2_client.get_client()
        key = f"temp/fal/{job_id}/{uuid.uuid4().hex}.{ext}"
        with open(local_path, "rb") as f:
            s3.put_object(
                Bucket=r2_client.config.R2_BUCKET_NAME,
                Body=f.read(),
                Key=key,
                ContentType=content_type,
            )
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": r2_client.config.R2_BUCKET_NAME, "Key": key},
            ExpiresIn=3600,
        )
    except Exception as exc:
        logger.exception("Fal temp R2 upload failed: %s", exc)
        return None


def _unwrap_fal_result(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "__dict__"):
        return {k: v for k, v in result.__dict__.items() if not k.startswith("_")}
    return {"raw": result}


def _fal_subscribe(model_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    fal = _import_fal_client()
    logger.info("Fal subscribe: %s", model_id)
    raw = fal.subscribe(model_id, arguments=arguments)
    return _unwrap_fal_result(raw)


def _extract_text_from_whisper(data: Dict[str, Any]) -> str:
    text = (data.get("text") or "").strip()
    if text:
        return text
    chunks = data.get("chunks") or data.get("segments") or []
    parts = []
    for c in chunks:
        if isinstance(c, dict):
            t = (c.get("text") or "").strip()
            if t:
                parts.append(t)
    return " ".join(parts).strip()


def _extract_audio_url(data: Dict[str, Any]) -> str:
    for key in ("audio_url", "url", "output_url"):
        v = data.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    audio = data.get("audio") or {}
    if isinstance(audio, dict):
        u = audio.get("url")
        if isinstance(u, str) and u.startswith("http"):
            return u
    return ""


def _base_lang(code: str) -> str:
    if not code:
        return "en"
    return code.split("-")[0].split("_")[0].lower()


def _translate_text(text: str, src: str, tgt: str) -> str:
    if not text or not str(text).strip():
        return ""
    s, t = _base_lang(src), _base_lang(tgt)
    if s == t:
        return text.strip()
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source=s, target=t).translate(text.strip())
    except Exception as exc:
        logger.warning("Translation fallback failed: %s", exc)
        return text.strip()


def _merge_audio_video(video_path: str, audio_path: str, out_path: str) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-i",
                audio_path,
                "-c:v",
                "copy",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-shortest",
                out_path,
            ],
            check=True,
            capture_output=True,
        )
        return os.path.isfile(out_path) and os.path.getsize(out_path) > 0
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning("ffmpeg mux failed: %s", exc)
        return False


def run_fal_dubbing_pipeline(
    *,
    job_id: str,
    user_id: str,
    media_url: str,
    target_lang: str,
    source_language: str = "",
    return_video: bool = True,
    engine: str = "",
) -> Dict[str, Any]:
    """
    Full Fal dubbing pipeline (blocking). Updates DB + Redis like Modal webhook.
    """
    if not is_fal_pipeline_configured():
        raise InferenceProviderError(
            "Fal pipeline not configured: set FAL_KEY and pip install fal-client"
        )

    job = DubbingJob.query.get(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")

    tmp = tempfile.mkdtemp(prefix=f"fal_dub_{job_id}_")
    duration_seconds = 0

    try:
        _publish_progress(job_id, "preparing", 0.05, "Downloading media")

        local_in = os.path.join(tmp, "input.bin")
        _download_media(media_url, local_in)

        is_video = return_video and _probe_is_video(local_in)
        audio_url_for_stt = media_url
        wav_path = os.path.join(tmp, "audio.wav")

        if is_video:
            if _extract_audio_wav(local_in, wav_path):
                up = _upload_temp_to_r2(wav_path, job_id, "wav", "audio/wav")
                if up:
                    audio_url_for_stt = up
            else:
                is_video = False
                logger.warning("[%s] ffmpeg missing — STT on original URL", job_id)
        elif local_in.lower().endswith((".wav", ".mp3", ".m4a", ".ogg")):
            shutil.copy(local_in, wav_path)
            up = _upload_temp_to_r2(wav_path, job_id, "wav", "audio/wav")
            if up:
                audio_url_for_stt = up

        src_lang = _base_lang(source_language or "auto")
        if src_lang == "auto":
            src_lang = "en"

        _publish_progress(job_id, "transcribing", 0.25, "Whisper STT (Fal)")
        whisper_args: Dict[str, Any] = {
            "audio_url": audio_url_for_stt,
            "task": "transcribe",
            "chunk_level": "segment",
        }
        if source_language and source_language not in ("auto", ""):
            whisper_args["language"] = _base_lang(source_language)

        whisper_out = _fal_subscribe(_fal_whisper_model(), whisper_args)
        transcript = _extract_text_from_whisper(whisper_out)
        if not transcript:
            raise RuntimeError("Whisper returned empty transcript")

        detected = whisper_out.get("language") or src_lang
        _publish_progress(
            job_id,
            "translating",
            0.45,
            "Translating",
            source=detected,
            target=target_lang,
        )
        translated = _translate_text(transcript, detected, target_lang)
        if not translated:
            raise RuntimeError("Translation produced empty text")

        _publish_progress(job_id, "synthesizing", 0.65, "TTS (Fal)")
        tts_lang = _base_lang(target_lang)
        tts_args: Dict[str, Any] = {
            "text": translated,
            "language": tts_lang,
        }
        tts_out = _fal_subscribe(_fal_tts_model(), tts_args)
        dubbed_audio_url = _extract_audio_url(tts_out)
        if not dubbed_audio_url:
            raise RuntimeError("Fal TTS returned no audio URL")

        dubbed_local = os.path.join(tmp, "dubbed.mp3")
        _download_media(dubbed_audio_url, dubbed_local)
        duration_seconds = max(1, int(_probe_duration_seconds(dubbed_local)))

        _publish_progress(job_id, "uploading", 0.85, "Uploading result")
        final_local = dubbed_local
        out_ext = "mp3"
        content_type = "audio/mpeg"

        if is_video and os.path.isfile(local_in):
            muxed = os.path.join(tmp, "output.mp4")
            if _merge_audio_video(local_in, dubbed_local, muxed):
                final_local = muxed
                out_ext = "mp4"
                content_type = "video/mp4"
            else:
                logger.warning("[%s] video mux failed — returning audio only", job_id)

        from shared import r2_client

        output_url = r2_client.upload_file(
            final_local,
            prefix=f"results/{job_id}",
            ext=out_ext,
        )
        if not output_url:
            key = f"results/{job_id}/{uuid.uuid4().hex}.{out_ext}"
            try:
                s3 = r2_client.get_client()
                extra = {"ContentType": content_type}
                s3.upload_file(final_local, r2_client.config.R2_BUCKET_NAME, key, ExtraArgs=extra)
                output_url = r2_client.generate_download_url(key)
            except Exception as exc:
                raise RuntimeError(f"R2 upload failed: {exc}") from exc

        if not output_url:
            raise RuntimeError("Could not upload dubbed output to R2")

        _publish_progress(job_id, "finalizing", 0.95, "Completing job")
        _complete_job(job, job_id, output_url, duration_seconds, user_id)

        logger.info("✅ Fal dubbing completed job %s → %s", job_id, output_url[:80])
        return {
            "success": True,
            "provider": "fal",
            "job_id": job_id,
            "output_url": output_url,
            "duration_seconds": duration_seconds,
        }

    except Exception as exc:
        logger.exception("❌ Fal dubbing failed job %s", job_id)
        _fail_job(job, job_id, str(exc))
        raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _probe_is_video(path: str) -> bool:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext in ("mp4", "mov", "mkv", "webm", "avi", "m4v"):
        return True
    try:
        out = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_type",
                "-of",
                "csv=p=0",
                path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return "video" in (out.stdout or "").lower()
    except FileNotFoundError:
        return ext in ("mp4", "mov", "mkv", "webm", "avi")


def _probe_duration_seconds(path: str) -> float:
    try:
        out = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return float((out.stdout or "0").strip() or 0)
    except Exception:
        return 8.0
