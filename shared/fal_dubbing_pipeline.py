# shared/fal_dubbing_pipeline.py — Fal.ai dubbing (STT → translate → TTS → R2)
"""
Runs in the Celery worker when INFERENCE_PROVIDER=fal.

Chains Fal models via fal_client.subscribe, updates dubbing_jobs (SQLAlchemy + Supabase),
and publishes Redis events for SSE (progress 50% → 100%).
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from shared.fal_lang_profiles import TargetLangProfile, resolve_target_language_profile
from shared.inference_provider import InferenceProviderError, _import_fal_client
from shared.job_events import publish_job_status
from shared.models import DubbingJob, db

logger = logging.getLogger(__name__)

# Fast STT (override with FAL_WHISPER_MODEL=fal-ai/whisper)
DEFAULT_FAL_WHISPER_MODEL = "fal-ai/wizper"
DEFAULT_FAL_TTS_PLAYHT = "fal-ai/playht/tts/v3"
DEFAULT_FAL_TTS_ELEVEN = "fal-ai/elevenlabs/tts/multilingual-v2"
DEFAULT_FAL_TTS_XTTS = "fal-ai/xtts"

FAL_PROGRESS_START = 50.0
FAL_PROGRESS_END = 100.0

# Reference clip for XTTS voice clone (seconds)
CLONE_SAMPLE_DURATION = float(os.environ.get("FAL_CLONE_SAMPLE_SECONDS", "12"))
CLONE_SAMPLE_START = float(os.environ.get("FAL_CLONE_SAMPLE_START", "0.5"))


def is_fal_pipeline_configured() -> bool:
    """True when FAL_KEY is set and fal-client imports."""
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


def _voice_config_dict(voice_config: Any) -> Dict[str, Any]:
    if isinstance(voice_config, dict):
        return voice_config
    return {}


def _voice_source(voice_config: Optional[Dict[str, Any]]) -> str:
    cfg = _voice_config_dict(voice_config)
    return (
        cfg.get("source")
        or cfg.get("voice_mode")
        or cfg.get("voice_source")
        or ""
    ).strip().lower()


def _wants_voice_clone(voice_config: Optional[Dict[str, Any]]) -> bool:
    """
    True when XTTS (or clone-capable TTS) should use a reference speaker clip.

    Frontend dubbing UI (dubbing.html):
      - voice_mode 'original' → "Voice Clone" — extract speaker from source media
      - voice_mode 'clone'    → premium Supabase voice (sample_file URL)
    """
    cfg = _voice_config_dict(voice_config)
    src = _voice_source(cfg)
    if src == "original":
        return True
    if src in ("clone", "cloned", "voice_clone"):
        return bool(_resolve_external_speaker_url(cfg))
    if cfg.get("voice_clone") or cfg.get("clone_voice"):
        return True
    return False


def _resolve_tts_model(
    engine: str,
    *,
    profile: TargetLangProfile,
    voice_clone: bool = False,
) -> str:
    """
    Pick Fal TTS model — mirrors Modal dubbing_factory Stage 5:
      - voice clone → xtts (like force_engine=xtts when voice_mode=clone)
      - Arabic non-clone → PlayHT (Modal default force_engine=piper for ar)
      - other langs → ElevenLabs multilingual v2
    """
    if voice_clone:
        return (
            os.environ.get("FAL_CLONE_TTS_MODEL")
            or DEFAULT_FAL_TTS_XTTS
        ).strip()

    explicit = (
        os.environ.get("FAL_TTS_MODEL")
        or os.environ.get("FAL_TTS_ENDPOINT")
        or ""
    ).strip()
    if explicit:
        return explicit

    eng = (engine or "").strip().lower()
    if eng in ("xtts", "clone", "cloned"):
        return DEFAULT_FAL_TTS_XTTS
    if eng in ("playht", "piper", "edge"):
        return DEFAULT_FAL_TTS_PLAYHT
    if eng in ("eleven", "elevenlabs"):
        return DEFAULT_FAL_TTS_ELEVEN

    if profile.base_lang == "ar":
        return DEFAULT_FAL_TTS_PLAYHT
    return DEFAULT_FAL_TTS_ELEVEN


def _map_progress(stage_pct: float) -> float:
    """Map stage 0–1 to frontend band 50–100%."""
    stage_pct = max(0.0, min(1.0, stage_pct))
    return FAL_PROGRESS_START + (FAL_PROGRESS_END - FAL_PROGRESS_START) * stage_pct


def _publish_progress(
    job_id: str,
    stage: str,
    stage_pct: float,
    message: Optional[str] = None,
    **extra: Any,
) -> None:
    pct = round(_map_progress(stage_pct), 1)
    payload: Dict[str, Any] = {
        "status": "processing",
        "stage": stage,
        "progress": pct,
        "provider": "fal",
    }
    if message:
        payload["message"] = message
    payload.update(extra)
    publish_job_status(job_id, payload)
    logger.info("[%s] Fal %s — %.0f%%", job_id, stage, pct)


def _patch_supabase_job(job_id: str, fields: Dict[str, Any]) -> bool:
    """Update dubbing_jobs in Supabase (service role)."""
    try:
        from shared.models import (
            complete_dubbing_job_supabase,
            fail_dubbing_job_supabase,
        )

        status = (fields.get("status") or "").strip().lower()
        if status == "completed":
            return complete_dubbing_job_supabase(
                job_id, (fields.get("output_url") or "").strip()
            )
        if status == "failed":
            return fail_dubbing_job_supabase(
                job_id, (fields.get("error") or "Fal dubbing failed")[:2000]
            )
    except ImportError:
        pass

    base = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
    service_key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
        or ""
    ).strip()
    if not base or not service_key:
        logger.warning("Supabase not configured — skipping dubbing_jobs PATCH for %s", job_id)
        return False

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    body = dict(fields)
    body.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
    try:
        res = requests.patch(
            f"{base}/rest/v1/dubbing_jobs",
            headers=headers,
            params={"id": f"eq.{job_id}"},
            json=body,
            timeout=15,
        )
        if res.ok:
            logger.info("Supabase dubbing_jobs %s updated: %s", job_id, list(body.keys()))
            return True
        logger.error(
            "Supabase PATCH failed for %s: HTTP %s %s",
            job_id,
            res.status_code,
            (res.text or "")[:400],
        )
    except requests.RequestException as exc:
        logger.exception("Supabase PATCH error for %s: %s", job_id, exc)
    return False


def _fail_job(job: DubbingJob, job_id: str, error: str) -> None:
    msg = (error or "Fal dubbing failed")[:2000]
    job.status = "failed"
    job.error = msg
    db.session.commit()
    _patch_supabase_job(job_id, {"status": "failed", "error": msg})
    publish_job_status(
        job_id,
        {
            "status": "failed",
            "error": msg,
            "progress": FAL_PROGRESS_START,
            "provider": "fal",
        },
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
    _patch_supabase_job(
        job_id,
        {"status": "completed", "output_url": output_url, "error": None},
    )
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


def _extract_voice_clone_sample(
    media_path: str,
    out_path: str,
    *,
    start_sec: float = CLONE_SAMPLE_START,
    duration_sec: float = CLONE_SAMPLE_DURATION,
) -> bool:
    """
    Extract a short, clean mono WAV from the source media for XTTS reference.
    Skips a brief lead-in, normalizes level, and band-limits speech frequencies.
    """
    total = _probe_duration_seconds(media_path)
    if total <= 0:
        total = duration_sec + start_sec + 1.0
    start = max(0.0, min(start_sec, max(0.0, total - 1.0)))
    clip_len = min(duration_sec, max(1.0, total - start))

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-t", f"{clip_len:.3f}",
                "-i", media_path,
                "-vn",
                "-af", "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar", "22050",
                "-ac", "1",
                out_path,
            ],
            check=True,
            capture_output=True,
        )
        ok = os.path.isfile(out_path) and os.path.getsize(out_path) > 0
        if ok:
            logger.info(
                "Voice clone sample: %.1fs from t=%.1fs (media %.1fs)",
                clip_len,
                start,
                total,
            )
        return ok
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning("Voice clone sample extract failed: %s", exc)
        return False


def _resolve_external_speaker_url(voice_config: Dict[str, Any]) -> Optional[str]:
    """Premium clone: use sample URL/file from voice_config if provided."""
    for key in ("sample_url", "sample_file", "file", "speaker_url"):
        val = (voice_config.get(key) or "").strip()
        if not val:
            continue
        if val.startswith("http://") or val.startswith("https://"):
            return val
        try:
            from shared import r2_client

            url = r2_client.generate_download_url(val)
            if url:
                return url
        except Exception as exc:
            logger.warning("Could not resolve sample key %s: %s", val[:80], exc)
    return None


def _prepare_speaker_reference_url(
    *,
    job_id: str,
    local_media_path: str,
    voice_config: Optional[Dict[str, Any]],
    tmp_dir: str,
) -> Optional[str]:
    """
    Build a public URL for XTTS reference audio: external sample or ffmpeg clip.
    Caller must delete tmp_dir (or individual files) when done.
    """
    cfg = _voice_config_dict(voice_config)
    external = _resolve_external_speaker_url(cfg)
    if external:
        logger.info("[%s] Using external speaker sample URL", job_id)
        return external

    src = _voice_source(cfg)
    if src not in ("original", "clone", "cloned", "voice_clone") and not (
        cfg.get("voice_clone") or cfg.get("clone_voice")
    ):
        return None

    sample_path = os.path.join(tmp_dir, "voice_clone_ref.wav")
    if not _extract_voice_clone_sample(local_media_path, sample_path):
        raise RuntimeError(
            "Voice clone requested but ffmpeg could not extract a reference sample "
            "(install ffmpeg/ffprobe on the worker)"
        )

    ref_url = _upload_temp_to_r2(sample_path, job_id, "wav", "audio/wav")
    if not ref_url:
        raise RuntimeError("Voice clone reference upload to R2 failed")
    logger.info("[%s] Uploaded voice clone reference for XTTS", job_id)
    return ref_url


def _extract_audio_wav(video_path: str, wav_path: str) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", video_path,
                "-vn", "-ar", "16000", "-ac", "1", wav_path,
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
        return r2_client.generate_download_url(key, expires_in=3600)
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
    for key in ("chunks", "segments", "output"):
        chunks = data.get(key)
        if isinstance(chunks, str) and chunks.strip():
            return chunks.strip()
        if isinstance(chunks, list):
            parts = []
            for c in chunks:
                if isinstance(c, dict):
                    t = (c.get("text") or "").strip()
                    if t:
                        parts.append(t)
            joined = " ".join(parts).strip()
            if joined:
                return joined
    return ""


def _extract_audio_url(data: Dict[str, Any]) -> str:
    for key in ("audio_url", "url", "output_url"):
        v = data.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    audio = data.get("audio") or data.get("file") or {}
    if isinstance(audio, dict):
        u = audio.get("url")
        if isinstance(u, str) and u.startswith("http"):
            return u
    return ""


def _base_lang(code: str) -> str:
    if not code or code.lower() == "auto":
        return "en"
    return code.split("-")[0].split("_")[0].lower()


def _translate_for_profile(
    text: str,
    src_lang: str,
    profile: TargetLangProfile,
) -> str:
    """
    Translate transcript toward target profile.

    Modal uses Claude + dialect for Arabic; Fal worker uses Google Translate to
    base_lang with dialect logged (regional flavor is primarily via TTS voice mapping).
    """
    if not text or not str(text).strip():
        return ""
    src = _base_lang(src_lang)
    tgt = profile.base_lang
    if src == tgt and not profile.dialect:
        return text.strip()
    try:
        from deep_translator import GoogleTranslator

        out = GoogleTranslator(source=src, target=tgt).translate(text.strip())
        if profile.dialect and profile.base_lang == "ar":
            logger.info(
                "Arabic translation via Google (base=%s, dialect=%s, code=%s)",
                tgt,
                profile.dialect,
                profile.lang_code,
            )
        return out
    except Exception as exc:
        logger.warning(
            "Translation failed (%s→%s, dialect=%s): %s",
            src,
            profile.lang_code,
            profile.dialect,
            exc,
        )
        return text.strip()


def _build_tts_arguments(
    model_id: str,
    text: str,
    profile: TargetLangProfile,
    *,
    speaker_reference_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Map text + dialect profile to Fal PlayHT / ElevenLabs / XTTS schemas."""
    mid = model_id.lower()
    lang = profile.tts_lang

    if "playht" in mid:
        voice = (
            os.environ.get(f"FAL_PLAYHT_VOICE_{profile.lang_code.replace('-', '_').upper()}")
            or os.environ.get("FAL_PLAYHT_VOICE")
            or profile.playht_voice
        ).strip()
        return {"input": text, "voice": voice}

    if "elevenlabs" in mid or "eleven" in mid:
        voice = (
            os.environ.get(f"FAL_ELEVEN_VOICE_{profile.lang_code.replace('-', '_').upper()}")
            or os.environ.get("FAL_ELEVEN_VOICE")
            or profile.eleven_voice
        ).strip()
        return {
            "text": text,
            "voice": voice,
            "language_code": profile.eleven_language_code,
        }

    if "xtts" in mid:
        ref = (speaker_reference_url or os.environ.get("FAL_XTTS_SPEAKER_URL") or "").strip()
        args: Dict[str, Any] = {
            "prompt": text,
            "text": text,
            "language": lang,
        }
        if ref:
            args["audio_url"] = ref
        return args

    return {"text": text, "language": lang, "language_code": profile.eleven_language_code}


def _merge_audio_video(video_path: str, audio_path: str, out_path: str) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
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


def _probe_is_video(path: str) -> bool:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext in ("mp4", "mov", "mkv", "webm", "avi", "m4v"):
        return True
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
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
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return float((out.stdout or "0").strip() or 0)
    except Exception:
        return 8.0


def _upload_result(final_local: str, job_id: str, out_ext: str, content_type: str) -> str:
    from shared import r2_client

    key = f"results/{job_id}/{uuid.uuid4().hex}.{out_ext}"
    if r2_client.upload_file_with_key(final_local, key, content_type=content_type):
        url = r2_client.generate_download_url(key)
        if url:
            return url
    url = r2_client.upload_file(
        final_local,
        prefix=f"results/{job_id}",
        ext=out_ext,
        content_type=content_type,
    )
    if url:
        return url
    raise RuntimeError("Could not upload dubbed output to R2")


def run_fal_dubbing_pipeline(
    job_id: str,
    user_id: str,
    media_url: str,
    target_lang: str,
    source_language: str,
    return_video: bool,
    engine: str,
    voice_config: Optional[Dict[str, Any]] = None,
    dialect: str = "",
) -> Dict[str, Any]:
    """
    Full Fal dubbing pipeline (blocking).

    1. Download media
    2. Fal Whisper/Wizper STT
    3. Translate to target_lang
    4. Fal TTS (PlayHT / ElevenLabs / XTTS by engine)
    5. Optional ffmpeg mux when return_video=True
    6. Upload to R2, mark job completed in DB + Supabase, SSE events
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
    voice_cfg = _voice_config_dict(voice_config)
    dialect_from_cfg = (voice_cfg.get("dialect") or dialect or "").strip()
    profile = resolve_target_language_profile(target_lang, dialect_from_cfg)
    voice_clone = _wants_voice_clone(voice_cfg)
    speaker_reference_url: Optional[str] = None

    logger.info(
        "[%s] Fal profile: code=%s base=%s dialect=%s edge=%s playht=%s eleven=%s clone=%s",
        job_id,
        profile.lang_code,
        profile.base_lang,
        profile.dialect or "(none)",
        profile.edge_voice,
        profile.playht_voice,
        profile.eleven_voice,
        voice_clone,
    )

    try:
        _publish_progress(job_id, "preparing", 0.05, "Downloading media")

        local_in = os.path.join(tmp, "input.bin")
        _download_media(media_url, local_in)

        if voice_clone:
            _publish_progress(
                job_id,
                "voice_sample",
                0.12,
                "Extracting speaker reference",
            )
            speaker_reference_url = _prepare_speaker_reference_url(
                job_id=job_id,
                local_media_path=local_in,
                voice_config=voice_cfg,
                tmp_dir=tmp,
            )
            if not speaker_reference_url:
                raise RuntimeError("Voice clone enabled but no speaker reference URL")

        is_video = bool(return_video) and _probe_is_video(local_in)
        audio_url_for_stt = media_url
        wav_path = os.path.join(tmp, "audio.wav")

        if is_video:
            if _extract_audio_wav(local_in, wav_path):
                up = _upload_temp_to_r2(wav_path, job_id, "wav", "audio/wav")
                if up:
                    audio_url_for_stt = up
            else:
                is_video = False
                logger.warning("[%s] ffmpeg unavailable — STT on original URL", job_id)
        elif local_in.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm")):
            shutil.copy(local_in, wav_path)
            up = _upload_temp_to_r2(wav_path, job_id, "wav", "audio/wav")
            if up:
                audio_url_for_stt = up

        _publish_progress(job_id, "transcribing", 0.2, "Speech-to-text (Fal)")
        whisper_args: Dict[str, Any] = {
            "audio_url": audio_url_for_stt,
            "task": "transcribe",
        }
        if "whisper" in _fal_whisper_model().lower():
            whisper_args["chunk_level"] = "segment"
        if source_language and source_language.lower() not in ("auto", ""):
            whisper_args["language"] = _base_lang(source_language)

        whisper_out = _fal_subscribe(_fal_whisper_model(), whisper_args)
        transcript = _extract_text_from_whisper(whisper_out)
        if not transcript:
            raise RuntimeError("Fal STT returned an empty transcript")

        detected = whisper_out.get("language") or _base_lang(source_language or "en")
        dialect_label = profile.dialect or profile.display_name or profile.lang_code
        _publish_progress(
            job_id,
            "translating",
            0.45,
            f"Translating ({dialect_label})",
            source=detected,
            target=profile.lang_code,
            dialect=profile.dialect,
        )
        translated = _translate_for_profile(transcript, detected, profile)
        if not translated:
            raise RuntimeError("Translation produced empty text")

        tts_model = _resolve_tts_model(engine, profile=profile, voice_clone=voice_clone)
        if voice_clone and "xtts" not in tts_model.lower():
            tts_model = DEFAULT_FAL_TTS_XTTS
        if voice_clone and not speaker_reference_url:
            raise RuntimeError("Voice clone requires a speaker reference URL for XTTS")

        clone_label = " (voice clone)" if voice_clone else ""
        voice_hint = profile.playht_voice if "playht" in tts_model else profile.eleven_voice
        _publish_progress(
            job_id,
            "synthesizing",
            0.65,
            f"TTS {profile.lang_code}{clone_label}",
            voice=voice_hint,
            dialect=profile.dialect,
        )
        tts_args = _build_tts_arguments(
            tts_model,
            translated,
            profile,
            speaker_reference_url=speaker_reference_url,
        )
        if voice_clone and not tts_args.get("audio_url"):
            raise RuntimeError(
                "XTTS voice clone missing audio_url — reference sample was not attached"
            )
        tts_out = _fal_subscribe(tts_model, tts_args)
        dubbed_audio_url = _extract_audio_url(tts_out)
        if not dubbed_audio_url:
            raise RuntimeError(f"Fal TTS ({tts_model}) returned no audio URL")

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

        output_url = _upload_result(final_local, job_id, out_ext, content_type)

        _publish_progress(job_id, "finalizing", 0.95, "Completing job")
        _complete_job(job, job_id, output_url, duration_seconds, user_id)

        logger.info("Fal dubbing completed job %s", job_id)
        return {
            "success": True,
            "provider": "fal",
            "job_id": job_id,
            "output_url": output_url,
            "duration_seconds": duration_seconds,
        }

    except Exception as exc:
        logger.exception("Fal dubbing failed job %s", job_id)
        _fail_job(job, job_id, str(exc))
        raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
